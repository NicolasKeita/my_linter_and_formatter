namespace NkLint;

internal static class SimilarFilenames
{
    internal static IEnumerable<LintDiagnostic> Analyze(IEnumerable<string> files, string scope)
    {
        if (scope is not ("directory" or "project"))
        {
            throw new ArgumentException("--similarity-scope requires directory or project");
        }
        var matches = new SortedDictionary<string, List<string>>(StringComparer.Ordinal);
        var groups = files.Select(Path.GetFullPath).Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(path => path, StringComparer.Ordinal)
            .GroupBy(path => scope == "directory" ? Path.GetDirectoryName(path) : "");

        foreach (var group in groups)
        {
            var paths = group.ToArray();

            for (var index = 0; index < paths.Length; index++)
            {
                foreach (var right in paths.Skip(index + 1))
                {
                    AddPair(matches, paths[index], right);
                }
            }
        }
        return matches.Select(pair => new LintDiagnostic(pair.Key, 1, 1, "NK013",
            "Similar filename(s): " + string.Join("; ", pair.Value.Order(StringComparer.Ordinal))
                + ". Prefer responsibility-based names."));
    }

    private static void AddPair(SortedDictionary<string, List<string>> matches, string left, string right)
    {
        if (Path.GetDirectoryName(left) != Path.GetDirectoryName(right)
            && Path.GetFileName(left) == Path.GetFileName(right)) return;

        var reason = NameComparison.Reason(Path.GetFileName(left), Path.GetFileName(right));

        if (reason is null) return;
        foreach (var (file, peer) in new[] { (left, right), (right, left) })
        {
            if (!matches.ContainsKey(file)) matches[file] = [];
            matches[file].Add($"{Path.GetRelativePath(Path.GetDirectoryName(file)!, peer)} ({reason})");
        }
    }
}
