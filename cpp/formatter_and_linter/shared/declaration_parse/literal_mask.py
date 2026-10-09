#!/usr/bin/env python3
"""
Length-preserving masking of literals and comments.

The masked text keeps the exact length of the input, so indexes computed on it
stay valid on the original text while braces, separators and parentheses hidden
inside literals no longer disturb the scans.
"""

ESCAPE = "\\"
BLOCK_COMMENT_START = "/*"
BLOCK_COMMENT_END = "*/"
QUOTE_CHARS = ('"', "'")


def _mask_quoted(chars: list[str], line: str, index: int) -> int:
    quote = line[index]
    chars[index] = " "
    index += 1
    length = len(line)
    while index < length:
        if line[index] == ESCAPE:
            chars[index] = " "
            if index + 1 < length:
                chars[index + 1] = " "
            index += 2
            continue
        chars[index] = " "
        if line[index] == quote:
            return index + 1
        index += 1
    return index


def _mask_block_comment(chars: list[str], line: str, index: int) -> int:
    end = line.find(BLOCK_COMMENT_END, index + 2)
    stop = len(line) if end == -1 else end + 2
    for position in range(index, stop):
        chars[position] = " "
    return stop


def mask_literals(line: str) -> str:
    """Replace string / char literals and inline block comments by spaces."""
    chars = list(line)
    index = 0
    length = len(line)
    while index < length:
        if line[index] in QUOTE_CHARS:
            index = _mask_quoted(chars, line, index)
            continue
        if line.startswith(BLOCK_COMMENT_START, index):
            index = _mask_block_comment(chars, line, index)
            continue
        index += 1
    return "".join(chars)
