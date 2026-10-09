#!/usr/bin/env python3
"""
Line-number helpers and the line collectors used by comment detection.

``line_number_at`` / ``line_at`` map a character offset onto the masked source.
The collectors walk the compiled patterns and return the sets of line numbers
holding functions, function bodies, plain declarations and template headers.
"""

import re

from shared.comment_utils.patterns import (
    EXCLUDED_DECLARATION_PATTERN,
    TEMPLATE_PREFIX_PATTERN,
    build_declaration_patterns,
    build_function_patterns,
)

EXCLUDED_MATCH = "curl_easy_setopt"


def line_number_at(code: str, pos: int) -> int:
    return code.count("\n", 0, pos) + 1


def line_at(code: str, pos: int) -> str:
    line_start = code.rfind("\n", 0, pos) + 1
    line_end = code.find("\n", pos)
    if line_end == -1:
        line_end = len(code)
    return code[line_start:line_end]


def _matching_brace_span(masked_code: str, brace_idx: int) -> range:
    depth = 0
    end_idx = len(masked_code) - 1
    for index in range(brace_idx, len(masked_code)):
        char = masked_code[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_idx = index
                break
    return range(
        line_number_at(masked_code, brace_idx),
        line_number_at(masked_code, end_idx) + 1,
    )


def find_function_body_lines(masked_code: str, match_starts: list[int]) -> set[int]:
    body_lines: set[int] = set()
    for start in match_starts:
        brace_idx = masked_code.find("{", start)
        semi_idx = masked_code.find(";", start)
        if brace_idx == -1 or (semi_idx != -1 and semi_idx < brace_idx):
            continue
        body_lines.update(_matching_brace_span(masked_code, brace_idx))
    return body_lines


def collect_function_lines(
    masked_code: str,
    comment_ranges: list[tuple[int, int]],
) -> tuple[set[int], list[int]]:
    def is_in_comment(pos: int) -> bool:
        return any(start <= pos < end for start, end in comment_ranges)

    function_lines: set[int] = set()
    match_starts: list[int] = []
    for pattern_str in build_function_patterns():
        for match in re.compile(pattern_str, re.MULTILINE).finditer(masked_code):
            if is_in_comment(match.start()):
                continue
            if EXCLUDED_MATCH in match.group().strip():
                continue
            function_lines.add(line_number_at(masked_code, match.start()))
            match_starts.append(match.start())
    return function_lines, match_starts


def collect_declaration_lines(
    masked_code: str,
    function_lines: set[int],
    function_body_lines: set[int],
) -> set[int]:
    declaration_lines: set[int] = set()
    for declaration_finder in build_declaration_patterns():
        for match in declaration_finder.finditer(masked_code):
            line_num = line_number_at(masked_code, match.start())
            if line_num in function_lines or line_num in function_body_lines:
                continue
            line_text = line_at(masked_code, match.start()).strip()
            if EXCLUDED_DECLARATION_PATTERN.match(line_text) or line_text.startswith("#"):
                continue
            declaration_lines.add(line_num)
    return declaration_lines


def collect_template_lines(
    masked_code: str,
    function_lines: set[int],
    declaration_lines: set[int],
) -> set[int]:
    template_lines: set[int] = set()
    for match in TEMPLATE_PREFIX_PATTERN.finditer(masked_code):
        line_num = line_number_at(masked_code, match.start())
        if (line_num + 1) in function_lines or (line_num + 1) in declaration_lines:
            template_lines.add(line_num)
    return template_lines
