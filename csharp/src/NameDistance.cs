using System.Text;

namespace NkLint;

internal static class NameDistance
{
    internal static int Measure(string left, string right)
    {
        var first = left.EnumerateRunes().ToArray();
        var second = right.EnumerateRunes().ToArray();
        var ceiling = first.Length + second.Length;
        var matrix = new int[first.Length + 2, second.Length + 2];
        var seen = new Dictionary<Rune, int>();

        matrix[0, 0] = ceiling;
        for (var row = 0; row <= first.Length; row++)
        {
            matrix[row + 1, 0] = ceiling;
            matrix[row + 1, 1] = row;
        }
        for (var column = 0; column <= second.Length; column++)
        {
            matrix[0, column + 1] = ceiling;
            matrix[1, column + 1] = column;
        }
        for (var row = 1; row <= first.Length; row++)
        {
            var matchedColumn = 0;

            for (var column = 1; column <= second.Length; column++)
            {
                var previousRow = seen.GetValueOrDefault(second[column - 1]);
                var previousColumn = matchedColumn;
                var cost = first[row - 1] == second[column - 1] ? 0 : 1;

                if (cost == 0) matchedColumn = column;
                matrix[row + 1, column + 1] = new[] {
                    matrix[row, column] + cost, matrix[row + 1, column] + 1,
                    matrix[row, column + 1] + 1,
                    matrix[previousRow, previousColumn] + row - previousRow + column - previousColumn - 1,
                }.Min();
            }
            seen[first[row - 1]] = row;
        }
        return matrix[first.Length + 1, second.Length + 1];
    }
}
