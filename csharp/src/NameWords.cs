using System.Text;

namespace NkLint;

internal static class NameWords
{
    private static string[] Split(string stem)
    {
        var characters = NameIdentity.Body(stem).EnumerateRunes().ToArray();
        var separated = new StringBuilder();

        for (var index = 0; index < characters.Length; index++)
        {
            var character = characters[index];
            var boundary = index > 0 && Rune.IsUpper(character)
                && (Rune.IsLower(characters[index - 1]) || Rune.IsDigit(characters[index - 1])
                    || (Rune.IsUpper(characters[index - 1]) && index + 1 < characters.Length
                        && Rune.IsLower(characters[index + 1])));

            if (boundary) separated.Append('_');
            separated.Append(character.ToString());
        }
        return separated.ToString().Split('_', StringSplitOptions.RemoveEmptyEntries)
            .Select(word => word.ToLowerInvariant()).ToArray();
    }

    internal static bool DifferingWordsMatch(string left, string right)
    {
        var first = Split(left);
        var second = Split(right);

        if (first.Length != second.Length || first.Length == 0) return false;
        for (var index = 0; index < first.Length; index++)
        {
            var word = first[index];
            var other = second[index];
            var wordLength = word.EnumerateRunes().Count();
            var otherLength = other.EnumerateRunes().Count();
            var length = Math.Max(wordLength, otherLength);

            if (word == other) continue;
            if (Math.Abs(wordLength - otherLength) * 100 > length * 15
                || NameDistance.Measure(word, other) * 100 > length * 15) return false;
        }
        return true;
    }
}
