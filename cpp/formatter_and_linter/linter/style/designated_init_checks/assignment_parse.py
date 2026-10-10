#!/usr/bin/env python3
"""Parsing of member assignments for the designated-init check."""

import re

from .patterns import DECLARATION_IDENTIFIER_RE

ASSIGN_OP_RE = r'\s*(?<![<>=!+\-*/%&|^])=(?!=)\s*'


def _find_top_level_semicolon(stripped_masked: str) -> int | None:
    """
    Return the index of the first top-level ';' (outside parentheses and
    braced initializers) in a masked line, or None when absent.
    """
    paren_depth = 0
    brace_depth = 0
    length = len(stripped_masked)
    i = 0

    while i < length:
        char = stripped_masked[i]
        if char == '(':
            paren_depth += 1
        elif char == ')':
            if paren_depth > 0:
                paren_depth -= 1
        elif char == '{':
            brace_depth += 1
        elif char == '}':
            if brace_depth > 0:
                brace_depth -= 1
        elif char == ';' and paren_depth == 0 and brace_depth == 0:
            return i
        i += 1

    return None


def _parse_member_assignment(
    stripped_masked: str,
    variable_name: str,
) -> tuple[str, str] | None:
    """
    Return (field_chain, rhs) when the masked, stripped line is a single
    plain assignment statement on a member of variable_name ('var.member = x;'
    or 'var.sub.member = x;'), or None otherwise. Compound assignments,
    comparisons, multiple statements on the line and trailing content after
    the terminating ';' are rejected.
    """
    semicolon_index = _find_top_level_semicolon(stripped_masked)
    if semicolon_index is None:
        return None

    if stripped_masked[semicolon_index + 1:].strip():
        return None

    head = stripped_masked[:semicolon_index]
    pattern = (
        rf'^(?P<lhs>{re.escape(variable_name)}'
        rf'(?:\s*\.\s*{DECLARATION_IDENTIFIER_RE})+)'
        rf'{ASSIGN_OP_RE}'
        rf'(?P<rhs>.+?)\s*$'
    )
    match = re.match(pattern, head)
    if match is None:
        return None

    lhs_body = match.group('lhs')[len(variable_name):]
    field_parts = [part.strip() for part in lhs_body.split('.')]
    field_chain = '.'.join(part for part in field_parts if part)
    if not field_chain:
        return None

    return field_chain, match.group('rhs')


def _references_variable(text: str, variable_name: str) -> bool:
    """
    Whether the masked text reads back the declared variable name as an
    identifier (word-boundary delimited, so 'var_count' does not count).
    """
    return re.search(rf'\b{re.escape(variable_name)}\b', text) is not None
