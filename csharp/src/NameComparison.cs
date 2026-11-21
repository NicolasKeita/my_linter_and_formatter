using System.Globalization;
using System.Text;

namespace NkLint;

internal static class NameComparison
{
    internal static string? Reason(string left, string right)
    {
        var leftStem = Path.GetFileNameWithoutExtension(left);
        var rightStem = Path.GetFileNameWithoutExtension(right);
        var first = NameIdentity.BaseName(leftStem);
        var second = NameIdentity.BaseName(rightStem);
        var firstLength = first.EnumerateRunes().Count();
        var secondLength = second.EnumerateRunes().Count();
        var length = Math.Max(firstLength, secondLength);

        if (!Path.GetExtension(left).Equals(Path.GetExtension(right), StringComparison.OrdinalIgnoreCase)
            || first.Length == 0 || second.Length == 0) return null;
        if (first == second) return "same normalized base (numbering, separators or case)";
        if (Math.Min(firstLength, secondLength) < 6
            || Math.Abs(firstLength - secondLength) * 100 > length * 15) return null;

        var distance = NameDistance.Measure(first, second);
        var percent = (100.0 * (length - distance) / length).ToString("F1", CultureInfo.InvariantCulture);

        return distance * 100 <= length * 15 && NameWords.DifferingWordsMatch(leftStem, rightStem)
            ? $"similarity {percent}% (global and differing words >=85%)" : null;
    }
}
