#!/usr/bin/env python3
"""Counting of effective (non-empty) lines inside a function body."""

from linter.module.cppm_inline_function_checks.header_classify import _line_of_position


def _line_bounds(sanitized: str, line_starts: list[int], line_number: int) -> tuple[int, int]:
    line_start = line_starts[line_number]
    if line_number + 1 < len(line_starts):
        return line_start, line_starts[line_number + 1] - 1
    return line_start, len(sanitized)


def _extract_segment(sanitized: str, bounds: dict) -> str:
    line_number = bounds["line_number"]
    open_line, open_pos = bounds["open"]
    close_line, close_pos = bounds["close"]
    line_start, line_end = bounds["line"]

    if line_number == open_line and line_number == close_line:
        return sanitized[open_pos + 1:close_pos]
    if line_number == open_line:
        return sanitized[open_pos + 1:line_end]
    if line_number == close_line:
        return sanitized[line_start:close_pos]
    return sanitized[line_start:line_end]


def _is_effective(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and stripped != '{' and stripped != '}'


def _count_effective_lines(
    sanitized: str,
    line_starts: list[int],
    open_pos: int,
    close_pos: int
) -> int:
    open_line = _line_of_position(line_starts, open_pos)
    close_line = _line_of_position(line_starts, close_pos)
    effective_lines = 0
    for line_number in range(open_line, close_line + 1):
        line_start, line_end = _line_bounds(sanitized, line_starts, line_number)
        bounds = {
            "line_number": line_number,
            "open": (open_line, open_pos),
            "close": (close_line, close_pos),
            "line": (line_start, line_end),
        }
        if _is_effective(_extract_segment(sanitized, bounds)):
            effective_lines += 1
    return effective_lines

