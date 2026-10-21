using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

namespace NkLint;

internal static class NameComparison
{
    private static readonly Regex Separators = new(@"[_\s\-\u2010-\u2015\u2212]+");
    private static readonly Regex Invisible = new(@"[\u200b-\u200d\u2060\ufeff]");
    private static readonly Regex NumberedEnd = new(@"(?:(?:part|chunk|split)[_\s-]*)?\p{Nd}+$");

    private static string BaseName(string stem)
    {
        var normalized = Invisible.Replace(stem.Normalize(NormalizationForm.FormKC).ToLowerInvariant(), "");
        var value = Separators.Replace(normalized, "_");

        while (true)
        {
            var previous = value;

            value = NumberedEnd.Replace(value.Trim('_'), "").Trim('_');
            if (value == previous) return value.Replace("_", "");
        }
    }

    internal static string? Reason(string left, string right)
    {
        var first = BaseName(Path.GetFileNameWithoutExtension(left));
        var second = BaseName(Path.GetFileNameWithoutExtension(right));
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

        return distance * 100 <= length * 15 ? $"similarity {percent}% (threshold 85%)" : null;
    }
}
