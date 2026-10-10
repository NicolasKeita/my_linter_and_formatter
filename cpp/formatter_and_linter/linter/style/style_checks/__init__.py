#!/usr/bin/env python3
"""
Style Checks

Checks for style violations in C++ code: line length, file length and
function length. The heavier rules live in focused submodules and are
re-exported here so existing ``from linter.style.style_checks import ...``
statements keep working.
"""

from .declaration_block import (
    _scan_body_for_declaration_block,
    check_blank_line_after_initialization,
)
from .declaration_classify import _is_declaration_line
from .function_length import (
    MAX_FUNCTION_LENGTH,
    check_function_length,
)
from .scanning import (
    _NON_DECLARATION_KEYWORD_RE,
    _mask_strings_and_comments,
)
from .signature_scan import (
    MAX_SIGNATURE_SCAN_LINES,
    _find_function_opening,
)

MAX_FILE_LENGTH = 120


def check_line_length(code: str, max_length: int = 120) -> list[tuple[int, int]]:
    lines = code.splitlines()
    long_lines = []
    for i, line in enumerate(lines, 1):
        if len(line) > max_length:
            long_lines.append((i, len(line)))
    return long_lines


def check_file_length(code: str, max_lines: int = MAX_FILE_LENGTH) -> tuple[bool, int]:
    line_count = len(code.splitlines())
    return (line_count > max_lines, line_count)


__all__ = [
    "MAX_FUNCTION_LENGTH",
    "MAX_FILE_LENGTH",
    "MAX_SIGNATURE_SCAN_LINES",
    "check_line_length",
    "check_file_length",
    "check_blank_line_after_initialization",
    "check_function_length",
    "_mask_strings_and_comments",
    "_NON_DECLARATION_KEYWORD_RE",
    "_scan_body_for_declaration_block",
    "_is_declaration_line",
    "_find_function_opening",
]
