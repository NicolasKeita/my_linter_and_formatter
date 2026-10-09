#!/usr/bin/env python3
"""
Splitting a raw source line into its code part and its trailing comment.

Line comments ('// ...') end the code part. Block comments are kept verbatim
inside the code part when they close on the same line; an unterminated block
comment makes the rest of the line the comment part and toggles the returned
state so the following lines stay neutral.
"""

from typing import NamedTuple

ESCAPE = "\\"
LINE_COMMENT = "//"
BLOCK_COMMENT_START = "/*"
BLOCK_COMMENT_END = "*/"

DOUBLE_QUOTE = '"'
SINGLE_QUOTE = "'"
QUOTES = (DOUBLE_QUOTE, SINGLE_QUOTE)


class LineSplit(NamedTuple):
    """A line split into its code part and its trailing comment."""

    code: str
    comment: str
    in_block_comment: bool


def _skip_quoted(line: str, index: int) -> int:
    quote = line[index]
    index += 1
    length = len(line)
    while index < length:
        if line[index] == ESCAPE:
            index += 2
            continue
        index += 1
        if line[index - 1] == quote:
            break
    return index


def _closed_block_comment(line: str, index: int) -> int | None:
    end = line.find(BLOCK_COMMENT_END, index + 2)
    return None if end == -1 else end + 2


def split_trailing_comment(line: str, in_block_comment: bool) -> LineSplit:
    """Split ``line`` into code, trailing comment and the new comment state."""
    index = 0
    length = len(line)
    code_end = 0
    while index < length:
        if in_block_comment:
            end = line.find(BLOCK_COMMENT_END, index)
            if end == -1:
                return LineSplit("", line, True)
            in_block_comment = False
            index = end + 2
            code_end = index
            continue
        if line[index] in QUOTES:
            index = _skip_quoted(line, index)
            code_end = index
            continue
        if line.startswith(LINE_COMMENT, index):
            return LineSplit(line[:code_end], line[index:], in_block_comment)
        if line.startswith(BLOCK_COMMENT_START, index):
            closed = _closed_block_comment(line, index)
            if closed is None:
                return LineSplit(line[:code_end], line[index:], True)
            index = closed
            code_end = index
            continue
        index += 1
        code_end = index
    return LineSplit(line[:code_end], "", in_block_comment)
