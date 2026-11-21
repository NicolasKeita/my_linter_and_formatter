using System.Text;
using System.Text.RegularExpressions;

namespace NkLint;

internal static class NameIdentity
{
    private static readonly Regex Separators = new(@"[_\s\-\u2010-\u2015\u2212]+");
    private static readonly Regex Invisible = new(@"[\u200b-\u200d\u2060\ufeff]");
    private static readonly Regex NumberedEnd = new(@"(?:(?:part|chunk|split)[_\s-]*)?\p{Nd}+$",
        RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

    internal static string Body(string stem)
    {
        var spelling = Invisible.Replace(stem.Normalize(NormalizationForm.FormKC), "");
        var value = Separators.Replace(spelling, "_");

        while (true)
        {
            var previous = value;

            value = NumberedEnd.Replace(value.Trim('_'), "").Trim('_');
            if (value == previous) return value;
        }
    }

    internal static string BaseName(string stem)
    {
        return Body(stem).Replace("_", "").ToLowerInvariant();
    }
}
