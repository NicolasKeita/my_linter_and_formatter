#!/usr/bin/env python3
"""Regexes and declaration parsing for the designated-init check."""

import re

from linter.style.style_checks import _NON_DECLARATION_KEYWORD_RE

DESIGNATED_INIT_MESSAGE = (
    "Warning [C++20-designated-init]: Préférez l'initialisation désignée "
    "'{suggestion}' plutôt qu'une initialisation vide suivie d'une affectation."
)

DECLARATION_QUALIFIERS_RE = (
    r'(?:(?:const|constexpr|consteval|constinit|static|inline|extern|mutable|'
    r'volatile|unsigned|signed|short|long|thread_local)\s+)*'
)

DECLARATION_TYPE_NAME_RE = r'[A-Za-z_]\w*(?:\s*::\s*[A-Za-z_]\w*)*'

DECLARATION_TEMPLATE_ARGS_RE = r'(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>\s*)?'

DECLARATION_POINTER_REFS_RE = r'(?:\s*[*&]\s*)*'

DECLARATION_IDENTIFIER_RE = r'[A-Za-z_]\w*'

_EMPTY_BRACE_DECL_RE = re.compile(
    rf'^(?P<type>{DECLARATION_QUALIFIERS_RE}'
    rf'{DECLARATION_TYPE_NAME_RE}'
    rf'{DECLARATION_TEMPLATE_ARGS_RE}'
    rf'{DECLARATION_POINTER_REFS_RE})'
    rf'\s*(?P<name>{DECLARATION_IDENTIFIER_RE})'
    r'\s*\{\s*\}\s*;\s*$'
)


def _is_blank_or_comment(stripped_masked: str) -> bool:
    """
    Whether a masked, stripped line should be skipped (empty or a comment).
    """
    return not stripped_masked or stripped_masked.startswith('//') or stripped_masked.startswith('/*')


def _parse_empty_brace_declaration(stripped_masked: str) -> tuple[str, str] | None:
    """
    Return (type, variable_name) when the masked statement is a single
    declaration with an empty-brace value initialization ('Type var{};'),
    or None otherwise. Non-empty braced initializers, designated
    initializers, parenthesized/copy initializations, multiple declarators
    and multi-statement lines are rejected.
    """
    if not stripped_masked.endswith(';'):
        return None

    if _NON_DECLARATION_KEYWORD_RE.match(stripped_masked):
        return None

    match = _EMPTY_BRACE_DECL_RE.match(stripped_masked)
    if match is None:
        return None

    return match.group('type').strip(), match.group('name')
