#!/usr/bin/env python3
"""
Multiple Variable Declaration Checks

Detects declarations of several variables on the same line, separated by
top-level commas (e.g. 'Type a, b;'). Commas inside template angle
brackets, function call parentheses or braced initializers are ignored.
"""

import re

from linter.style.style_checks import _NON_DECLARATION_KEYWORD_RE, _mask_strings_and_comments

MULTIPLE_VAR_DECL_MESSAGE = "[MULTIPLE_VAR_DECL] Declare only one variable per line."

_DECLARED_IDENTIFIER_RE = re.compile(r'\s*[&*]*\s*[A-Za-z_]\w*\s*(?:=|;|,|\(|\[|\{|$)')

_OPEN_DEPTH_INDEX = {'(': 0, '<': 1, '{': 2}
_CLOSE_DEPTH_INDEX = {')': 0, '>': 1, '}': 2}


def _apply_depth_change(char: str, depths: list[int]) -> None:
    """Open or close one nesting level of ``char`` in ``depths``
    (parentheses at index 0, angle brackets at 1, braces at 2)."""
    if char in _OPEN_DEPTH_INDEX:
        depths[_OPEN_DEPTH_INDEX[char]] += 1
    elif char in _CLOSE_DEPTH_INDEX:
        slot = _CLOSE_DEPTH_INDEX[char]
        if depths[slot] > 0:
            depths[slot] -= 1


def _scan_line_for_top_level_comma(line: str, initial_paren_depth: int = 0) -> tuple[bool, int]:
    """
    Check whether a masked code line contains a comma at declaration level
    (outside parentheses, template angle brackets and braced initializers)
    followed by something that looks like a declared identifier.

    The parenthesis depth starts at initial_paren_depth so that call
    arguments opened on previous lines (multi-line function calls) are not
    mistaken for top-level commas. Returns whether such a comma was found
    and the parenthesis depth reached at end of line, so callers can carry
    it over to continuation lines.
    """
    depths = [initial_paren_depth, 0, 0]
    length = len(line)
    i = 0

    while i < length:
        char = line[i]
        _apply_depth_change(char, depths)
        if char == ',' and not any(depths):
            if _DECLARED_IDENTIFIER_RE.match(line[i + 1:]):
                return True, depths[0]
        i += 1

    return False, depths[0]


def _has_top_level_declaration_comma(line: str, initial_paren_depth: int = 0) -> bool:
    """
    Check whether a masked code line contains a comma at declaration level
    (outside parentheses, template angle brackets and braced initializers)
    followed by something that looks like a declared identifier.
    """
    has_top_level_comma, _ = _scan_line_for_top_level_comma(line, initial_paren_depth)
    return has_top_level_comma


def check_multiple_var_declarations(code: str) -> list[int]:
    """
    Report lines declaring several variables separated by top-level commas.

    Returns a list of 1-based line numbers. Strings, comments, template
    argument lists, function call arguments and braced initializer lists are
    excluded from detection. The parenthesis depth is carried across lines so
    that continuation lines of multi-line calls or parenthesized expressions
    are never mistaken for top-level declarations.
    """
    lines = code.splitlines()
    violations: list[int] = []
    in_block_comment = False
    paren_depth = 0

    for line_index, raw_line in enumerate(lines):
        masked_line, in_block_comment = _mask_strings_and_comments(raw_line, in_block_comment)
        stripped = masked_line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        has_top_level_comma, paren_depth = _scan_line_for_top_level_comma(stripped, paren_depth)
        if _NON_DECLARATION_KEYWORD_RE.match(stripped):
            continue
        if not stripped.endswith(';'):
            continue
        if has_top_level_comma:
            violations.append(line_index + 1)

    return violations
