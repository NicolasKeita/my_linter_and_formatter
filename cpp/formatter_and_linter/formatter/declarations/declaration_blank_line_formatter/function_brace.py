#!/usr/bin/env python3
"""Detection of a function definition's opening brace in a C++ source line."""

import re

from shared.brace_utils import (
    extract_function_name,
    find_brace_positions,
    is_initializer_list,
    is_lambda_capture,
)
from shared.function_analysis import find_function_start_for_brace

_CONTROL_BLOCK_RE = re.compile(r'\b(class|struct|enum|namespace|do|else|try)\b')


def _prev_nonempty(lines: list[str], idx: int) -> str:
    j = idx - 1
    while j >= 0:
        stripped = lines[j].strip()
        if stripped:
            return stripped
        j -= 1
    return ''


def is_function_open_brace(line: str, lines: list[str], idx: int) -> bool:
    """
    Return True when ``line`` carries the opening brace of a function
    definition (same-line brace or a lone ``{`` preceded by a signature).
    """
    positions = find_brace_positions(line)
    if not any(char == '{' for _, char in positions):
        return False

    for pos, char in positions:
        if char != '{':
            continue
        before = line[:pos]
        if is_lambda_capture(line, pos):
            continue
        if is_initializer_list(line, pos):
            continue
        local_paren_depth = before.count('(') - before.count(')')
        if local_paren_depth == 0 and '(' in before:
            if extract_function_name(before) is not None:
                return True

    stripped = line.strip()
    if stripped == '{':
        previous = _prev_nonempty(lines, idx)
        if not previous or _CONTROL_BLOCK_RE.search(previous):
            return False
        return find_function_start_for_brace(lines, idx) is not None

    return False
