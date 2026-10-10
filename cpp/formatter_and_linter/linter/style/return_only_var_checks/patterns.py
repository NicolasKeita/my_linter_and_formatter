#!/usr/bin/env python3
"""Patterns and line classification helpers for the return-only variable check."""

import re

from linter.style.multiple_var_decl_checks import _has_top_level_declaration_comma
from linter.style.style_checks import _NON_DECLARATION_KEYWORD_RE

RETURN_ONLY_VAR_MESSAGE = (
    "Variable '{name}' déclarée uniquement pour être retournée immédiatement. "
    "Préférer un 'return' direct de l'expression."
)

_DECLARATION_QUALIFIERS_RE = (
    r'(?:(?:const|constexpr|consteval|constinit|static|inline|extern|mutable|'
    r'volatile|unsigned|signed|short|long|thread_local)\s+)*'
)

_DECLARATION_TYPE_NAME_RE = r'[A-Za-z_]\w*(?:\s*::\s*[A-Za-z_]\w*)*'

_DECLARATION_TEMPLATE_ARGS_RE = r'(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>\s*)?'

_DECLARATION_POINTER_REFS_RE = r'(?:\s*[*&]\s*)*'

_DECLARATOR_NAME_RE = r'(?P<name>[A-Za-z_]\w*)'

_INITIALIZED_DECL_RE = re.compile(
    rf'^{_DECLARATION_QUALIFIERS_RE}'
    rf'(?:auto\s+|{_DECLARATION_TYPE_NAME_RE}{_DECLARATION_TEMPLATE_ARGS_RE})'
    rf'{_DECLARATION_POINTER_REFS_RE}'
    rf'\s*{_DECLARATOR_NAME_RE}\s*'
    rf'(?:\{{|\(|=)'
)

_RETURN_VAR_RE = re.compile(r'^return\s+(?P<name>[A-Za-z_]\w*)\s*;\s*$')


def _is_blank_or_comment(stripped_masked: str) -> bool:
    """
    Whether a masked, stripped line should be skipped (empty or comment).
    """
    return not stripped_masked or stripped_masked.startswith('//') or stripped_masked.startswith('/*')


def _top_level_semicolon_index(stripped_masked: str) -> int | None:
    """
    Return the index of the first top-level ';' (outside parentheses and
    outside the braced initializer) in a masked line, or None when absent.
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


def _is_single_complete_declaration(stripped_masked: str) -> bool:
    """
    Whether a masked, stripped line is a single complete initialized
    declaration: it terminates with a top-level ';', nothing executable follows
    that ';' on the same line, and there is no top-level comma (which would
    indicate multiple declarators such as 'auto a = 1, b = 2;').
    """
    semi_index = _top_level_semicolon_index(stripped_masked)
    if semi_index is None:
        return False

    if stripped_masked[semi_index + 1:].strip() != '':
        return False

    if _has_top_level_declaration_comma(stripped_masked[:semi_index + 1]):
        return False

    return True


def _parse_initialized_declaration(stripped_masked: str) -> str | None:
    """
    Return the declared variable name when the masked statement starts a
    local variable declaration with initialization (braced, parenthesized or
    copy initialization), or None otherwise.

    The statement does not need to be complete on a single line: only the
    declarator prefix is matched here, multi-line completion is handled by the
    caller.
    """
    if _NON_DECLARATION_KEYWORD_RE.match(stripped_masked):
        return None

    match = _INITIALIZED_DECL_RE.match(stripped_masked)
    if match is None:
        return None

    return match.group('name')
