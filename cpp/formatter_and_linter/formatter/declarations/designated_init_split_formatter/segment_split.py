#!/usr/bin/env python3
"""Splitting of a designated-initializer statement line into several lines."""

import re

from .initializer_scan import _find_initializer

FIELD_INDENT = 4

_DESIGNATED_FIELD = re.compile(r"^\s*\.[A-Za-z_]\w*\s*(?:=|\{)")


def _copy_string(text: str, i: int, current: list[str]) -> int:
    """Append the string literal opening at ``text[i]`` to ``current``,
    honouring backslash escapes; returns the index just past the closing
    quote, or the end of ``text`` when the literal is unterminated."""
    quote = text[i]
    current.append(quote)
    i += 1
    length = len(text)
    while i < length:
        char = text[i]
        current.append(char)
        i += 1
        if char == "\\" and i < length:
            current.append(text[i])
            i += 1
            continue
        if char == quote:
            break
    return i


def _split_top_level_commas(text: str) -> list[str]:
    """
    Split ``text`` on its top-level commas only; commas nested inside
    parentheses, brackets, braces or angle brackets are preserved.
    """
    segments: list[str] = []
    current: list[str] = []
    depth = 0
    i = 0
    length = len(text)
    while i < length:
        char = text[i]
        if char in ('"', "'"):
            i = _copy_string(text, i, current)
            continue
        if char in "([{<":
            depth += 1
        elif char in ")]}>":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            segments.append("".join(current))
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    segments.append("".join(current))
    return segments


def _has_designated_initializer(segments: list[str]) -> bool:
    """Tell whether any top-level segment starts with a designated field."""
    return any(_DESIGNATED_FIELD.match(segment) for segment in segments)


def _split_statement_line(line: str) -> list[str]:
    """
    Split one over-long designated-initializer declaration line into several
    lines, or return the line unchanged when it is not splittable.
    """
    found = _find_initializer(line)
    if found is None:
        return [line]
    open_index, close_index, name_column, semicolon_index = found
    segments = _split_top_level_commas(line[open_index + 1:close_index])
    if not _has_designated_initializer(segments):
        return [line]
    field_indent = " " * (name_column + FIELD_INDENT)
    closing_indent = " " * name_column
    trailing = line[semicolon_index + 1:]
    lines = [line[:open_index + 1]]
    for segment in segments:
        stripped = segment.strip()
        if stripped:
            lines.append(field_indent + stripped + ",")
    closing = closing_indent + "};"
    if trailing.strip():
        closing += trailing
    lines.append(closing)
    return lines
