#!/usr/bin/env python3
"""Function-length rule: report functions longer than the allowed line count."""

from .brace_scanner import BraceScanner
from .signature_scan import _find_function_opening

MAX_FUNCTION_LENGTH = 40


def _close_functions_at_scope(
    open_functions: list[tuple[int, str, int]],
    scope_depth: int,
    line_index: int,
    max_lines: int,
    long_functions: list[tuple[str, int, int]],
) -> None:
    """Pop and record functions whose scope just closed at ``scope_depth``."""
    while open_functions and open_functions[-1][0] == scope_depth:
        _, func_name, start_line = open_functions.pop()
        function_lines = line_index - start_line + 1
        if function_lines > max_lines:
            long_functions.append((func_name, start_line + 1, function_lines))


def check_function_length(code: str, max_lines: int = MAX_FUNCTION_LENGTH) -> list[tuple[str, int, int]]:
    """
    Report functions longer than max_lines as (name, start_line, line_count)
    tuples. Function signatures spanning several lines are supported: each
    opening brace at parenthesis depth zero is classified as a function body
    or another scope (control structure, namespace, class, block), and the
    function length is measured from its signature start line to its closing
    brace line.
    """
    lines = code.splitlines()
    long_functions: list[tuple[str, int, int]] = []
    open_functions: list[tuple[int, str, int]] = []
    scanner = BraceScanner(lines)

    for line_index, _, head, is_open in scanner.iter_braces():
        if is_open:
            opening = _find_function_opening(lines, line_index, head)
            scanner.scope_depth += 1
            if opening is not None:
                func_name, start_line = opening
                open_functions.append((scanner.scope_depth - 1, func_name, start_line))
        else:
            if scanner.scope_depth > 0:
                scanner.scope_depth -= 1
            _close_functions_at_scope(
                open_functions, scanner.scope_depth, line_index, max_lines, long_functions
            )

    return long_functions
