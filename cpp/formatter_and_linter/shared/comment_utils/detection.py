#!/usr/bin/env python3
"""
Function / declaration / comment classification for C++ source lines.

``detect_comments_and_functions`` reports, for a source file, which lines hold a
comment (and which flavour), which lines belong to a function signature or body
and which lines hold a plain declaration. The result feeds the placement check
implemented in :mod:`shared.comment_utils.placement`.

All pattern matching runs on a length-preserving masked copy of the source so
string / char literals and comments never produce false matches, while line
numbers still map one-to-one onto the original text.
"""

from functools import partial

from shared.comment_utils.comment_entries import collect_comment_entries
from shared.comment_utils.line_classification import (
    collect_declaration_lines,
    collect_function_lines,
    collect_template_lines,
    find_function_body_lines,
    line_number_at,
)
from shared.comment_utils.scanning import scan_string_and_comment_ranges


def mask_literals_and_comments(code: str, ranges: list[tuple[int, int]]) -> str:
    """Blank out every character covered by ``ranges`` but keep line breaks."""
    masked = list(code)
    for start, end in ranges:
        for index in range(start, end):
            if masked[index] != "\n":
                masked[index] = " "
    return "".join(masked)


def detect_comments_and_functions(code: str) -> tuple[list[tuple[int, str]], set[int], set[int]]:
    """Classify every line of ``code`` as comment, function or declaration."""
    string_ranges, comment_ranges = scan_string_and_comment_ranges(code)
    masked_code = mask_literals_and_comments(code, string_ranges + comment_ranges)

    function_lines, match_starts = collect_function_lines(masked_code, comment_ranges)
    function_body_lines = find_function_body_lines(masked_code, match_starts)
    declaration_lines = collect_declaration_lines(masked_code, function_lines, function_body_lines)
    function_lines |= collect_template_lines(masked_code, function_lines, declaration_lines)

    comments = collect_comment_entries(code, comment_ranges, partial(line_number_at, code))
    return comments, function_lines, declaration_lines
