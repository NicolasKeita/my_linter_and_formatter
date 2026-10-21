namespace NkLint;

internal static class DirectoryChecks
{
    private const int MaxSubdirectories = 8;

    private static readonly HashSet<string> IgnoredNames = new(StringComparer.OrdinalIgnoreCase)
    {
        ".git", ".vs", "bin", "obj", "node_modules", "TestResults",
    };

    internal static IEnumerable<(string Path, string[] Children)> Enumerate(string root)
    {
        var pending = new Stack<string>();

        pending.Push(root);
        while (pending.Count > 0)
        {
            var directory = pending.Pop();
            var children = Directory.EnumerateDirectories(directory)
                .Where(child => !IgnoredNames.Contains(Path.GetFileName(child)))
                .ToArray();
            yield return (directory, children);
            foreach (var child in children)
            {
                pending.Push(child);
            }
        }
    }

    internal static IEnumerable<LintDiagnostic> Analyze(string root)
    {
        foreach (var (directory, children) in Enumerate(root))
        {
            if (children.Length > MaxSubdirectories)
            {
                yield return new LintDiagnostic(directory, 1, 1, "NK012",
                    $"{children.Length} sous-dossiers directs (maximum : {MaxSubdirectories}).");
            }
        }
    }
}
