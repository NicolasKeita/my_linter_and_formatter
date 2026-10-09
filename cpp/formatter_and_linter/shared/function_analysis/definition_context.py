#!/usr/bin/env python3
"""
Deciding whether a brace opens a function body.

`is_function_definition_context` handles the common case (name visible on the
brace line); `check_multiline_function_signature` walks upwards when the
signature spans several lines and the opening parenthesis is on an earlier one.
"""

from shared.brace_utils import extract_function_name, is_control_structure
from shared.function_analysis.stream_operators import has_stream_operators

SKIPPABLE_LINE_PREFIXES = (":", ",")


def is_function_definition_context(
    lines: list[str],
    line_idx: int,
    brace_line: str,
    paren_depth: int,
    angle_depth: int,
) -> bool:
    if paren_depth != 0 or angle_depth != 0:
        return False
    if is_control_structure(brace_line):
        return False
    func_name = extract_function_name(brace_line)
    if func_name is None:
        return check_multiline_function_signature(lines, line_idx)
    return True


def _skip_continuation_line(line: str) -> bool:
    if not line or line.startswith("//") or line == "{":
        return True
    if line.startswith(SKIPPABLE_LINE_PREFIXES):
        return True
    return has_stream_operators(line)


def _closes_opening_paren(line: str, paren_depth: int) -> tuple[bool, int]:
    """Scan ``line`` backwards and report whether it closes an outer group."""
    for char in reversed(line):
        if char == ")":
            paren_depth += 1
        elif char == "(":
            paren_depth -= 1
            if paren_depth < 0:
                return True, paren_depth
    return False, paren_depth


def check_multiline_function_signature(lines: list[str], line_idx: int) -> bool:
    """Look upwards for the opening parenthesis of the current signature."""
    paren_depth = 0
    for i in range(line_idx - 1, -1, -1):
        line = lines[i].strip()
        if _skip_continuation_line(line):
            continue
        balanced, paren_depth = _closes_opening_paren(line, paren_depth)
        if balanced:
            return extract_function_name(line) is not None
        if line.endswith(";") or (line.endswith("}") and line != "{"):
            return False
    return False
