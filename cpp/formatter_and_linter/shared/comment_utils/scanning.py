#!/usr/bin/env python3
"""
Low-level scanner for C++ string and comment ranges.

``scan_string_and_comment_ranges`` walks the source once and reports the
half-open character ranges covered by string / char literals and by ``//`` and
``/* */`` comments. ``remove_comments`` / ``restore_comments`` swap comments for
placeholders (and back) so the other passes can work on comment-free code.
"""

from shared.comment_utils.literal_scanners import (
    raw_string_prefix_start,
    scan_block_comment,
    scan_char_literal,
    scan_line_comment,
    scan_raw_string,
    scan_string_literal,
)

COMMENT_PLACEHOLDER = "___COMMENT_{}___"


def _scan_string_at(code: str, index: int, length: int) -> tuple[int, int] | None:
    prefix_start = raw_string_prefix_start(code, index)
    if prefix_start != -1:
        scanned = scan_raw_string(code, index, prefix_start)
        if scanned is not None:
            return scanned
    return scan_string_literal(code, index, length)


def scan_string_and_comment_ranges(code: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return the literal ranges and the comment ranges found in ``code``."""
    length = len(code)
    string_ranges: list[tuple[int, int]] = []
    comment_ranges: list[tuple[int, int]] = []
    index = 0
    while index < length:
        char = code[index]
        following = code[index + 1] if index + 1 < length else ""
        if char == "/" and following == "/":
            start, end = scan_line_comment(code, index, length)
            comment_ranges.append((start, end))
            index = end
            continue
        if char == "/" and following == "*":
            start, end = scan_block_comment(code, index, length)
            comment_ranges.append((start, end))
            index = end
            continue
        if char == '"':
            scanned = _scan_string_at(code, index, length)
        elif char == "'":
            scanned = scan_char_literal(code, index, length)
        else:
            scanned = None
        if scanned is not None:
            start, end = scanned
            string_ranges.append((start, end))
            index = end
            continue
        index += 1
    return string_ranges, comment_ranges


def remove_comments(code: str) -> tuple[str, list[str]]:
    """Replace every comment by a placeholder and return the removed texts."""
    comments: list[str] = []
    _, comment_ranges = scan_string_and_comment_ranges(code)
    parts: list[str] = []
    cursor = 0
    for start, end in sorted(comment_ranges):
        parts.append(code[cursor:start])
        parts.append(COMMENT_PLACEHOLDER.format(len(comments)))
        comments.append(code[start:end])
        cursor = end
    parts.append(code[cursor:])
    return "".join(parts), comments


def restore_comments(code: str, comments: list[str]) -> str:
    """Put back the comments previously removed by :func:`remove_comments`."""
    for i, comment in enumerate(comments):
        code = code.replace(COMMENT_PLACEHOLDER.format(i), comment)
    return code
