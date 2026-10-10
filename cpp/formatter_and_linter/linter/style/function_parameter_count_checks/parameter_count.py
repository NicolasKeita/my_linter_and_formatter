#!/usr/bin/env python3
"""Counting of top-level parameters in a function signature header."""

from linter.module.cppm_inline_function_checks import _find_parameter_list_paren


def _extract_parameter_list(normalized: str, paren_index: int) -> str:
    """Return the parameter list between the parenthesis at ``paren_index``
    and its matching close, or '' when the list never closes."""
    depth = 0
    close_index = -1
    for i in range(paren_index, len(normalized)):
        char = normalized[i]
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                close_index = i
                break
    if close_index == -1:
        return ''
    return normalized[paren_index + 1:close_index].strip()


def _count_top_level_commas(param_list: str) -> int:
    """Count the commas of ``param_list`` that are not nested inside
    parentheses, angle brackets, square brackets or braces."""
    count = 1
    paren_depth = 0
    angle_depth = 0
    bracket_depth = 0
    brace_depth = 0
    for char in param_list:
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth = max(0, paren_depth - 1)
        elif char == '<':
            angle_depth += 1
        elif char == '>':
            angle_depth = max(0, angle_depth - 1)
        elif char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth = max(0, bracket_depth - 1)
        elif char == '{':
            brace_depth += 1
        elif char == '}':
            brace_depth = max(0, brace_depth - 1)
        elif (char == ','
              and paren_depth == 0
              and angle_depth == 0
              and bracket_depth == 0
              and brace_depth == 0):
            count += 1
    return count


def _count_parameters(header: str) -> int:
    """
    Return the number of parameters declared in a function signature header.

    The header is normalised (whitespace collapsed) before the parameter
    list is extracted from the first top-level parenthesis pair. Empty
    lists '()' and the C-style '(void)' yield zero. Top-level commas are
    counted; commas nested inside parentheses, angle brackets, square
    brackets and braces are ignored.
    """
    normalized = ' '.join(header.split())
    paren_index = _find_parameter_list_paren(normalized)
    if paren_index == -1:
        return 0
    param_list = _extract_parameter_list(normalized, paren_index)
    if not param_list or param_list == 'void':
        return 0
    return _count_top_level_commas(param_list)
