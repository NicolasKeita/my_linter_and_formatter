using System.Diagnostics;

namespace NkLint;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length == 0 || args[0] is "help" or "--help" or "-h")
        {
            PrintHelp();
            return args.Length == 0 ? 2 : 0;
        }

        if (args.Length != 2 && args.Length != 4)
        {
            PrintHelp();
            return 2;
        }

        try
        {
            var target = Path.GetFullPath(args[1]);
            var similarityScope = args.Length == 4 ? args[3] : "directory";

            if (args.Length == 4 && (args[2] != "--similarity-scope" || args[0] is not ("lint" or "check"))
                || similarityScope is not ("directory" or "project"))
            {
                throw new ArgumentException("--similarity-scope requires directory or project (lint/check only)");
            }

            return args[0] switch
            {
                "lint" => Lint(target, similarityScope),
                "format" => Format(target, verify: false),
                "check" => Check(target, similarityScope),
                "init" => InstallConfig(target),
                _ => UnknownCommand(args[0]),
            };
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or ArgumentException)
        {
            Console.Error.WriteLine(exception.Message);
            return 2;
        }
    }

    private static int UnknownCommand(string command)
    {
        Console.Error.WriteLine($"Commande inconnue : {command}");
        PrintHelp();
        return 2;
    }

    private static int Lint(string target, string similarityScope)
    {
        if (!File.Exists(target) && !Directory.Exists(target))
        {
            throw new FileNotFoundException($"Chemin introuvable : {target}");
        }

        if (File.Exists(target) && !IsWorkspace(target)
            && !Path.GetExtension(target).Equals(".cs", StringComparison.OrdinalIgnoreCase))
        {
            throw new ArgumentException("Le linter accepte un fichier .cs, un projet, une solution ou un dossier.");
        }

        var diagnostics = LintRunner.Analyze(target, similarityScope);
        foreach (var diagnostic in diagnostics.OrderBy(item => item.Path)
                     .ThenBy(item => item.Line)
                     .ThenBy(item => item.Column)
                     .ThenBy(item => item.Code))
        {
            var label = Path.GetRelativePath(Environment.CurrentDirectory, diagnostic.Path);
            Console.WriteLine(
                $"{label}({diagnostic.Line},{diagnostic.Column}): {diagnostic.Code} {diagnostic.Message}");
        }

        Console.WriteLine($"{diagnostics.Count} problème(s).");
        return diagnostics.Count == 0 ? 0 : 1;
    }

    private static int Check(string target, string similarityScope)
    {
        var workspace = FindWorkspace(target);
        var formatResult = Format(workspace, verify: true);
        var lintResult = Lint(workspace, similarityScope);

        return formatResult == 0 && lintResult == 0 ? 0 : 1;
    }

    private static int Format(string target, bool verify)
    {
        var workspace = FindWorkspace(target);
        var start = new ProcessStartInfo("dotnet")
        {
            UseShellExecute = false,
        };

        start.ArgumentList.Add("format");
        start.ArgumentList.Add(workspace);
        if (verify)
        {
            start.ArgumentList.Add("--verify-no-changes");
        }

        using var process = Process.Start(start)
            ?? throw new IOException("Impossible de démarrer dotnet format.");
        process.WaitForExit();
        return process.ExitCode;
    }

    private static string FindWorkspace(string target)
    {
        if (File.Exists(target) && IsWorkspace(target))
        {
            return target;
        }

        if (!Directory.Exists(target))
        {
            throw new ArgumentException("Le formatage exige un dossier, un .sln, un .slnx ou un .csproj.");
        }

        var workspaces = Directory.EnumerateFiles(target)
            .Where(IsWorkspace)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();
        if (workspaces.Length != 1)
        {
            throw new ArgumentException(
                $"Le dossier {target} contient {workspaces.Length} projet/solution à sa racine ; "
                + "indiquez explicitement un .sln, .slnx ou .csproj.");
        }

        return workspaces[0];
    }

    private static bool IsWorkspace(string path)
    {
        return Path.GetExtension(path).ToLowerInvariant() is ".sln" or ".slnx" or ".csproj";
    }

    private static int InstallConfig(string target)
    {
        if (!Directory.Exists(target))
        {
            throw new DirectoryNotFoundException($"Dossier introuvable : {target}");
        }

        var destination = Path.Combine(target, ".editorconfig");
        if (File.Exists(destination))
        {
            throw new IOException($"Le fichier {destination} existe déjà. Fusionnez les réglages manuellement.");
        }

        var source = Path.Combine(AppContext.BaseDirectory, ".editorconfig");
        File.Copy(source, destination);
        Console.WriteLine($"Configuration créée : {destination}");
        return 0;
    }

    private static void PrintHelp()
    {
        Console.WriteLine("nk-csharp <lint|format|check|init> <chemin>");
        Console.WriteLine("  lint/check : --similarity-scope directory|project (défaut : directory)");
        Console.WriteLine("  lint    Analyse un fichier .cs, un dossier, un projet ou une solution.");
        Console.WriteLine("  format  Exécute dotnet format sur un .csproj/.sln/.slnx.");
        Console.WriteLine("  check   Vérifie le formatage sans écrire, puis analyse le code.");
        Console.WriteLine("  init    Copie .editorconfig dans un projet (sans écraser un fichier existant).");
    }
}
