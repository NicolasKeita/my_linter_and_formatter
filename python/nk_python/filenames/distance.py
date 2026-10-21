"""Unrestricted Damerau-Levenshtein distance, including adjacent transpositions."""


def edit_distance(left: str, right: str) -> int:
    ceiling = len(left) + len(right)
    matrix = [[0] * (len(right) + 2) for _ in range(len(left) + 2)]
    matrix[0][0] = ceiling
    for row in range(len(left) + 1):
        matrix[row + 1][0], matrix[row + 1][1] = ceiling, row
    for column in range(len(right) + 1):
        matrix[0][column + 1], matrix[1][column + 1] = ceiling, column
    seen: dict[str, int] = {}
    for row, character in enumerate(left, 1):
        matched_column = 0
        for column, other in enumerate(right, 1):
            previous_row = seen.get(other, 0)
            previous_column = matched_column
            cost = int(character != other)
            if cost == 0:
                matched_column = column
            matrix[row + 1][column + 1] = min(
                matrix[row][column] + cost,
                matrix[row + 1][column] + 1,
                matrix[row][column + 1] + 1,
                matrix[previous_row][previous_column] + row - previous_row + column - previous_column - 1,
            )
        seen[character] = row
    return matrix[-1][-1]
