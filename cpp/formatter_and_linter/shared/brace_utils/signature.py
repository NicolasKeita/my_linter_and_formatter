#!/usr/bin/env python3
"""
Function-name extraction from a single signature line.

``extract_function_name`` returns the identifier that precedes the parameter
list, or ``None`` when the line is not a plain function signature (control
statement, initializer, assignment, ...).
"""

from shared.brace_utils.keywords import CONTROL_KEYWORDS

_SIGNATURE_HEAD_FORBIDDEN_CHARS = frozenset({"{", "}", ";", "=", "'", '"'})
_OPEN_PAREN = "("
_QUOTE_CHARS = ('"', "'")
ESCAPE = "\\"


def _find_first_outer_paren(text: str) -> int:
    """Index of the first '(' outside any string / char literal, or -1."""
    in_string = False
    string_char = ""
    i = 0
    length = len(text)
    while i < length:
        char = text[i]
        if in_string:
            if char == ESCAPE:
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in _QUOTE_CHARS:
            in_string = True
            string_char = char
            i += 1
            continue
        if char == _OPEN_PAREN:
            return i
        i += 1
    return -1


def _is_identifier_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def _trailing_identifier(before_paren: str) -> str | None:
    name_end = len(before_paren)
    name_start = name_end - 1
    while name_start >= 0 and _is_identifier_char(before_paren[name_start]):
        name_start -= 1
    name_start += 1
    if name_start >= name_end:
        return None
    return before_paren[name_start:name_end]


def extract_function_name(line: str) -> str | None:
    stripped = line.strip()
    paren_pos = _find_first_outer_paren(stripped)
    if paren_pos == -1:
        return None
    before_paren = stripped[:paren_pos].rstrip()
    if not before_paren:
        return None
    if any(char in _SIGNATURE_HEAD_FORBIDDEN_CHARS for char in before_paren):
        return None
    func_name = _trailing_identifier(before_paren)
    if func_name is None or func_name in CONTROL_KEYWORDS:
        return None
    return func_name
