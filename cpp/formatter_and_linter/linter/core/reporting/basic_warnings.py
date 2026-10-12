#!/usr/bin/env python3
"""Reporting for line length, comment placement, header and length warnings."""

import sys

from linter.core.reporting._path_label import get_path_label
from linter.style.style_checks import MAX_FILE_LENGTH, MAX_FUNCTION_LENGTH


def print_issue_header(file_path: str) -> None:
    path_label = get_path_label(file_path)
    print(f"\n{path_label}", file=sys.stderr)


def print_line_length_warnings(long_lines: list[tuple[int, int]], max_length: int = 120) -> None:
    for line_num, actual_length in long_lines:
        print(f"⚠️  Line {line_num} exceeds {max_length} characters: {actual_length} characters", file=sys.stderr)


def print_comment_placement_warnings(invalid_comments: list[tuple[int, str]]) -> None:
    messages = {
        "singleline": "Single-line comment not above a function or declaration",
        "inline": "Inline comment not allowed (only comments above functions or declarations are permitted)",
        "multiline_start": "Multiline comment not above a function or declaration",
        "multiline_content": "Multiline comment content not above a function or declaration",
    }
    for line_num, comment_type in invalid_comments:
        message = messages.get(comment_type)
        if message:
            print(f"⚠️  Line {line_num}: {message}", file=sys.stderr)


def _print_file_too_long(line_count: int, max_lines: int) -> None:
    detail = f"File exceeds {max_lines} lines: {line_count} lines. "
    advice = "Split into multiple smaller files with explicit, coherent names."
    print(f"⚠️  {detail}{advice}", file=sys.stderr)


def print_file_length_warning(exceeds_limit: bool, line_count: int, max_lines: int = MAX_FILE_LENGTH) -> None:
    if exceeds_limit:
        _print_file_too_long(line_count, max_lines)


def _format_function_length_detail(
    func_name: str,
    start_line: int,
    line_count: int,
    max_lines: int,
) -> str:
    location = f"Function '{func_name}' at line {start_line} "
    return location + f"exceeds {max_lines} lines: {line_count} lines"


def print_function_length_warnings(
    long_functions: list[tuple[str, int, int]],
    max_lines: int = MAX_FUNCTION_LENGTH,
) -> None:
    for func_name, start_line, line_count in long_functions:
        detail = _format_function_length_detail(func_name, start_line, line_count, max_lines)
        print(f"⚠️  {detail}", file=sys.stderr)
