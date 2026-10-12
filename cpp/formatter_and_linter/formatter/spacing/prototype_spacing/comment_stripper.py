#!/usr/bin/env python3
"""Comment stripping that keeps string and character literals intact."""


def _skip_string_literal(line: str, index: int, quote: str, result: list[str]) -> int:
    """Consume a string/char literal starting at the opening quote."""
    length = len(line)
    result.append(quote)
    index += 1
    while index < length:
        if line[index] == "\\" and index + 1 < length:
            index += 2
            continue
        if line[index] == quote:
            index += 1
            break
        index += 1
    result.append(quote)
    return index


def _strip_line_comments(line: str, in_block_comment: bool) -> tuple[str, bool]:
    result: list[str] = []
    index = 0
    length = len(line)

    while index < length:
        if in_block_comment:
            end = line.find("*/", index)
            if end == -1:
                index = length
            else:
                in_block_comment = False
                index = end + 2
            continue

        if line.startswith("//", index):
            break

        if line.startswith("/*", index):
            in_block_comment = True
            index += 2
            continue

        char = line[index]
        if char == '"' or char == "'":
            index = _skip_string_literal(line, index, char, result)
            continue

        result.append(char)
        index += 1

    return "".join(result), in_block_comment


def strip_comments(lines: list[str]) -> list[str]:
    code_lines = []
    in_block_comment = False

    for line in lines:
        stripped_line, in_block_comment = _strip_line_comments(line, in_block_comment)
        code_lines.append(stripped_line)

    return code_lines
