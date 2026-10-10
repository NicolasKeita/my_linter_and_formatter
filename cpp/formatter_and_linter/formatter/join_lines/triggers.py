#!/usr/bin/env python3
"""Line-level trigger detection and scanning helpers for the join pass."""

from .patterns import (
    _END_SINGLE,
    _END_TOKENS,
    _START_SINGLE,
    _START_TOKENS,
)


def _ends_with_trigger(text: str) -> bool:
    for token in _END_TOKENS:
        if text.endswith(token):
            return True
    return bool(text) and text[-1] in _END_SINGLE


def _starts_with_trigger(text: str) -> bool:
    for token in _START_TOKENS:
        if text.startswith(token):
            return True
    return bool(text) and text[0] in _START_SINGLE


def _has_line_comment(line: str) -> bool:
    in_string = False
    string_char = ""
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        if in_string:
            if char == "\\":
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue
        if char == "/" and i + 1 < length and line[i + 1] == "/":
            return True
        i += 1
    return False


def _count_logical_operators(line: str) -> int:
    """Count '&&' and '||' operators outside string/char literals."""
    in_string = False
    string_char = ""
    count = 0
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        if in_string:
            if char == "\\":
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue
        if line[i:i + 2] in ("&&", "||"):
            count += 1
            i += 2
            continue
        i += 1
    return count


def _starts_logical_chain(line: str) -> bool:
    return line.lstrip().startswith(("&&", "||"))


def _ends_logical_chain(line: str) -> bool:
    return line.rstrip().endswith(("&&", "||"))


def _is_statement_continuation(line_a: str, line_b: str) -> bool:
    """Return True when two consecutive lines belong to the same wrapped statement."""
    a = line_a.rstrip()
    b = line_b.strip()
    if not a or not b:
        return False
    if a.lstrip().startswith("#") or b.startswith("#"):
        return False
    if _has_line_comment(a) or _has_line_comment(b):
        return False
    return _ends_with_trigger(a) or _starts_with_trigger(b)
