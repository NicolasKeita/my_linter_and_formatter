using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace NkLint;

internal sealed record LintDiagnostic(string Path, int Line, int Column, string Code, string Message);

internal static class LintRunner
{
    private const int MaxLineLength = 120;
    private const int MaxFileLines = 400;
    private const int MaxCallableLines = 40;
    private const int MaxParameters = 5;
    private const int MaxFilesPerDirectory = 10;

    private static readonly HashSet<string> IgnoredDirectories = new(StringComparer.OrdinalIgnoreCase)
    {
        ".git", ".vs", "bin", "obj", "node_modules", "TestResults",
    };

    internal static List<LintDiagnostic> Analyze(string target)
    {
        var result = new List<LintDiagnostic>();
        var files = Path.GetExtension(target).ToLowerInvariant() switch
        {
            ".csproj" => ProjectSources.FromProject(target),
            ".sln" or ".slnx" => ProjectSources.FromSolution(target),
            _ => EnumerateSourceFiles(target)
                .Select(path => new SourceFile(path, new CSharpParseOptions(LanguageVersion.Latest)))
                .ToArray(),
        };
        var selected = files.Where(file => !IsGenerated(file.Path))
            .DistinctBy(file => (file.Path.ToUpperInvariant(),
                string.Join(';', file.Options.PreprocessorSymbolNames)))
            .OrderBy(file => file.Path, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        foreach (var file in selected)
        {
            AnalyzeFile(file, result);
        }

        if (!File.Exists(target) || !Path.GetExtension(target).Equals(".cs", StringComparison.OrdinalIgnoreCase))
        {
            foreach (var group in selected.Select(file => file.Path)
                         .Distinct(StringComparer.OrdinalIgnoreCase)
                         .GroupBy(Path.GetDirectoryName))
            {
                if (group.Count() > MaxFilesPerDirectory && group.Key is not null)
                {
                    result.Add(new LintDiagnostic(group.Key, 1, 1, "NK011",
                        $"{group.Count()} fichiers .cs directs (maximum : {MaxFilesPerDirectory})."));
                }
            }
        }

        return result.Distinct().ToList();
    }

    private static IEnumerable<string> EnumerateSourceFiles(string target)
    {
        if (File.Exists(target))
        {
            if (Path.GetExtension(target).Equals(".cs", StringComparison.OrdinalIgnoreCase))
            {
                if (!IsGenerated(target))
                {
                    yield return target;
                }

                yield break;
            }

            target = Path.GetDirectoryName(target)!;
        }

        var pending = new Stack<string>();
        pending.Push(target);
        while (pending.Count > 0)
        {
            var directory = pending.Pop();
            foreach (var file in Directory.EnumerateFiles(directory, "*.cs"))
            {
                if (!IsGenerated(file))
                {
                    yield return file;
                }
            }

            foreach (var child in Directory.EnumerateDirectories(directory))
            {
                if (!IgnoredDirectories.Contains(Path.GetFileName(child)))
                {
                    pending.Push(child);
                }
            }
        }
    }

    private static bool IsGenerated(string path)
    {
        var name = Path.GetFileName(path);

        return name.EndsWith(".g.cs", StringComparison.OrdinalIgnoreCase)
            || name.EndsWith(".generated.cs", StringComparison.OrdinalIgnoreCase)
            || name.EndsWith(".Designer.cs", StringComparison.OrdinalIgnoreCase)
            || name.EndsWith(".AssemblyInfo.cs", StringComparison.OrdinalIgnoreCase);
    }

    private static void AnalyzeFile(SourceFile file, List<LintDiagnostic> result)
    {
        var path = file.Path;
        var source = File.ReadAllText(path);
        var tree = CSharpSyntaxTree.ParseText(source, file.Options, path: path);
        var root = tree.GetCompilationUnitRoot();

        if (root.Members.Count == 0 && root.Usings.Count == 0
            && root.Externs.Count == 0 && root.AttributeLists.Count == 0)
        {
            Add(result, 0, tree, "NK010", "Fichier sans code C#.");
        }

        AnalyzeSize(source, tree, result);

        foreach (var error in tree.GetDiagnostics().Where(item => item.Severity == DiagnosticSeverity.Error))
        {
            var span = error.Location.GetLineSpan();
            result.Add(new LintDiagnostic(path, span.StartLinePosition.Line + 1,
                span.StartLinePosition.Character + 1, "NK000", error.GetMessage()));
        }

        var bodies = new List<SyntaxNode>();
        AnalyzeCallables(path, tree, root, result, bodies);
        AnalyzeComments(path, tree, root, result, bodies);
        AnalyzeMultipleDeclarations(path, tree, root, result);
        AnalyzeReturns(path, tree, root, result);
    }

    private static void AnalyzeSize(string source, SyntaxTree tree, List<LintDiagnostic> result)
    {
        var lines = tree.GetText().Lines;
        var lineCount = lines.Count - (source.EndsWith('\n') ? 1 : 0);

        if (lineCount > MaxFileLines)
        {
            Add(result, 0, tree, "NK002",
                $"Fichier de {lineCount} lignes (maximum : {MaxFileLines}).");
        }

        for (var index = 0; index < lines.Count; index++)
        {
            var line = lines[index].ToString();
            if (line.Length > MaxLineLength)
            {
                Add(result, lines[index].Start + MaxLineLength, tree, "NK001",
                    $"Ligne de {line.Length} caractères (maximum : {MaxLineLength}).");
            }
        }
    }

    private static void AnalyzeCallables(string path, SyntaxTree tree, CompilationUnitSyntax root,
        List<LintDiagnostic> result, List<SyntaxNode> bodies)
    {
        foreach (var method in root.DescendantNodes().OfType<BaseMethodDeclarationSyntax>())
        {
            var parameters = method switch
            {
                MethodDeclarationSyntax item => item.ParameterList.Parameters.Count,
                ConstructorDeclarationSyntax item => item.ParameterList.Parameters.Count,
                OperatorDeclarationSyntax item => item.ParameterList.Parameters.Count,
                ConversionOperatorDeclarationSyntax item => item.ParameterList.Parameters.Count,
                _ => 0,
            };
            if (method.Body is null && method.ExpressionBody is null)
            {
                continue;
            }

            CheckParameters(path, tree, method, parameters, result);
            CheckBody(path, tree, (SyntaxNode?)method.Body ?? method.ExpressionBody, result, bodies);
        }

        foreach (var local in root.DescendantNodes().OfType<LocalFunctionStatementSyntax>())
        {
            CheckParameters(path, tree, local, local.ParameterList.Parameters.Count, result);
            CheckBody(path, tree, (SyntaxNode?)local.Body ?? local.ExpressionBody, result, bodies);
        }

        foreach (var accessor in root.DescendantNodes().OfType<AccessorDeclarationSyntax>())
        {
            CheckBody(path, tree, (SyntaxNode?)accessor.Body ?? accessor.ExpressionBody, result, bodies);
        }

        AnalyzeLambdas(path, tree, root, result, bodies);
    }

    private static void AnalyzeLambdas(string path, SyntaxTree tree, CompilationUnitSyntax root,
        List<LintDiagnostic> result, List<SyntaxNode> bodies)
    {
        foreach (var lambda in root.DescendantNodes().OfType<AnonymousFunctionExpressionSyntax>())
        {
            var parameters = lambda switch
            {
                ParenthesizedLambdaExpressionSyntax item => item.ParameterList.Parameters.Count,
                AnonymousMethodExpressionSyntax item => item.ParameterList?.Parameters.Count ?? 0,
                _ => 1,
            };

            CheckParameters(path, tree, lambda, parameters, result);
            CheckBody(path, tree, lambda.Body, result, bodies);
        }
    }

    private static void CheckParameters(string path, SyntaxTree tree, SyntaxNode declaration, int count,
        List<LintDiagnostic> result)
    {
        if (count > MaxParameters)
        {
            Add(result, declaration.SpanStart, tree, "NK004",
                $"Définition avec {count} paramètres (maximum : {MaxParameters}).");
        }
    }

    private static void CheckBody(string path, SyntaxTree tree, SyntaxNode? body,
        List<LintDiagnostic> result, List<SyntaxNode> bodies)
    {
        if (body is null)
        {
            return;
        }

        var span = body.GetLocation().GetLineSpan();
        var lineCount = span.EndLinePosition.Line - span.StartLinePosition.Line + 1;
        if (lineCount > MaxCallableLines)
        {
            Add(result, body.SpanStart, tree, "NK003",
                $"Corps de {lineCount} lignes (maximum : {MaxCallableLines}).");
        }

        bodies.Add(body);
        if (body is BlockSyntax block)
        {
            CheckBlankLineAfterDeclarations(path, tree, block, result);
        }
    }

    private static void CheckBlankLineAfterDeclarations(string path, SyntaxTree tree, BlockSyntax body,
        List<LintDiagnostic> result)
    {
        var statements = body.Statements;
        var count = 0;

        while (count < statements.Count && statements[count] is LocalDeclarationStatementSyntax)
        {
            count++;
        }

        if (count == 0 || count == statements.Count)
        {
            return;
        }

        var lastDeclaration = statements[count - 1];
        var followingStatement = statements[count];
        var lastLine = lastDeclaration.GetLocation().GetLineSpan().EndLinePosition.Line;
        var nextLine = followingStatement.GetLocation().GetLineSpan().StartLinePosition.Line;
        if (nextLine - lastLine < 2)
        {
            Add(result, lastDeclaration.SpanStart, tree, "NK008",
                "Ajoutez une ligne vide après les déclarations locales initiales.");
        }
    }

    private static void AnalyzeComments(string path, SyntaxTree tree, CompilationUnitSyntax root,
        List<LintDiagnostic> result, List<SyntaxNode> bodies)
    {
        var lines = tree.GetText().Lines;

        foreach (var trivia in root.DescendantTrivia(descendIntoTrivia: true))
        {
            if (!trivia.IsKind(SyntaxKind.SingleLineCommentTrivia)
                && !trivia.IsKind(SyntaxKind.MultiLineCommentTrivia))
            {
                continue;
            }

            if (bodies.Any(body => body.Span.Contains(trivia.SpanStart)))
            {
                Add(result, trivia.SpanStart, tree, "NK006",
                    "Placez les commentaires hors du corps des fonctions.");
            }

            var position = tree.GetLineSpan(trivia.Span).StartLinePosition;
            var prefix = lines[position.Line].ToString()[..position.Character];
            if (!string.IsNullOrWhiteSpace(prefix))
            {
                Add(result, trivia.SpanStart, tree, "NK007",
                    "Placez le commentaire sur une ligne distincte.");
            }
        }
    }

    private static void AnalyzeMultipleDeclarations(string path, SyntaxTree tree, CompilationUnitSyntax root,
        List<LintDiagnostic> result)
    {
        foreach (var declaration in root.DescendantNodes().OfType<VariableDeclarationSyntax>())
        {
            if (declaration.Variables.Count > 1
                && declaration.Parent is LocalDeclarationStatementSyntax
                    or FieldDeclarationSyntax
                    or EventFieldDeclarationSyntax)
            {
                Add(result, declaration.SpanStart, tree, "NK005",
                    "Déclarez une seule variable par instruction.");
            }
        }
    }

    private static void AnalyzeReturns(string path, SyntaxTree tree, CompilationUnitSyntax root,
        List<LintDiagnostic> result)
    {
        foreach (var block in root.DescendantNodes().OfType<BlockSyntax>())
        {
            for (var index = 0; index + 1 < block.Statements.Count; index++)
            {
                if (block.Statements[index] is not LocalDeclarationStatementSyntax local
                    || !local.UsingKeyword.IsKind(SyntaxKind.None)
                    || local.Declaration.Variables.Count != 1
                    || local.Declaration.Variables[0].Initializer is null
                    || block.Statements[index + 1] is not ReturnStatementSyntax returned
                    || returned.Expression is not IdentifierNameSyntax identifier
                    || identifier.Identifier.ValueText != local.Declaration.Variables[0].Identifier.ValueText)
                {
                    continue;
                }

                Add(result, local.SpanStart, tree, "NK009",
                    $"Retournez directement l'expression au lieu de créer '{identifier.Identifier.ValueText}'.");
            }
        }
    }

    private static void Add(List<LintDiagnostic> result, int offset, SyntaxTree tree,
        string code, string message)
    {
        var position = tree.GetLineSpan(new Microsoft.CodeAnalysis.Text.TextSpan(offset, 0)).StartLinePosition;

        result.Add(new LintDiagnostic(tree.FilePath, position.Line + 1, position.Character + 1, code, message));
    }
}
