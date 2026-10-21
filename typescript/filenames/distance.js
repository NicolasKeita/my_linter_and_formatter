export function editDistance(left, right) {
  const first = Array.from(left);
  const second = Array.from(right);
  const ceiling = first.length + second.length;
  const matrix = Array.from({ length: first.length + 2 }, () => Array(second.length + 2).fill(0));

  matrix[0][0] = ceiling;
  for (let row = 0; row <= first.length; row += 1) {
    matrix[row + 1][0] = ceiling;
    matrix[row + 1][1] = row;
  }
  for (let column = 0; column <= second.length; column += 1) {
    matrix[0][column + 1] = ceiling;
    matrix[1][column + 1] = column;
  }
  const seen = new Map();

  for (let row = 1; row <= first.length; row += 1) {
    let matchedColumn = 0;

    for (let column = 1; column <= second.length; column += 1) {
      const previousRow = seen.get(second[column - 1]) ?? 0;
      const previousColumn = matchedColumn;
      const cost = Number(first[row - 1] !== second[column - 1]);

      if (cost === 0) {
        matchedColumn = column;
      }
      matrix[row + 1][column + 1] = Math.min(
        matrix[row][column] + cost,
        matrix[row + 1][column] + 1,
        matrix[row][column + 1] + 1,
        matrix[previousRow][previousColumn] + row - previousRow + column - previousColumn - 1,
      );
    }
    seen.set(first[row - 1], row);
  }
  return matrix[first.length + 1][second.length + 1];
}
