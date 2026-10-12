#!/usr/bin/env python3
"""Header classification and line-offset helpers for the cppm scanner."""

import bisect
import re

from linter.module.cppm_inline_function_checks.block_model import _BlockKind
from linter.module.cppm_inline_function_checks.patterns import (
    _ACCESS_LABEL_PATTERN,
    _CONTROL_KEYWORDS,
    _FUNCTION_NAME_PATTERN,
    _LEADING_WHITESPACE_PATTERN,
    _NAMESPACE_KEYWORD_PATTERN,
    _TYPE_DECLARATION_PATTERN,
    _TYPE_KEYWORD_PATTERN,
    _WHITESPACE_RUN_PATTERN,
)


def _compute_line_starts(code: str) -> list[int]:
    starts = [0]
    for match in re.finditer('\n', code):
        starts.append(match.end())
    return starts


def _line_of_position(line_starts: list[int], position: int) -> int:
    return bisect.bisect_right(line_starts, position) - 1


def _split_header(header: str) -> tuple[str, int]:
    offset = 0
    while True:
        label_match = _ACCESS_LABEL_PATTERN.match(header, offset)
        if not label_match:
            break
        offset = label_match.end()
    whitespace_match = _LEADING_WHITESPACE_PATTERN.match(header, offset)
    offset = whitespace_match.end()
    return header[offset:], offset


def _find_parameter_list_paren(header: str) -> int:
    template_depth = 0
    for index, char in enumerate(header):
        if char == '<':
            template_depth += 1
        elif char == '>':
            template_depth = max(0, template_depth - 1)
        elif char == '(' and template_depth == 0:
            return index
    return -1


def _classify_header(header: str) -> tuple[_BlockKind, str]:
    normalized = ' '.join(header.split())
    if not normalized or normalized.startswith('#'):
        return _BlockKind.OTHER, ''
    if _NAMESPACE_KEYWORD_PATTERN.search(normalized):
        return _BlockKind.NAMESPACE, ''
    if _TYPE_DECLARATION_PATTERN.search(normalized):
        return _BlockKind.TYPE, ''
    paren_index = _find_parameter_list_paren(normalized)
    if paren_index == -1:
        if _TYPE_KEYWORD_PATTERN.search(normalized):
            return _BlockKind.TYPE, ''
        return _BlockKind.OTHER, ''
    name_match = _FUNCTION_NAME_PATTERN.search(normalized[:paren_index])
    if not name_match:
        return _BlockKind.OTHER, ''
    name = _WHITESPACE_RUN_PATTERN.sub('', name_match.group(0))
    if name.split('::')[-1] in _CONTROL_KEYWORDS:
        return _BlockKind.OTHER, ''
    return _BlockKind.FUNCTION, name


def _is_braced_initializer(code: str, segment_start: int, brace_index: int) -> bool:
    if brace_index == 0:
        return False
    previous = code[brace_index - 1]
    if not (previous.isalnum() or previous == '_'):
        return False
    header = code[segment_start:brace_index]
    if _NAMESPACE_KEYWORD_PATTERN.search(header) or _TYPE_KEYWORD_PATTERN.search(header):
        return False
    last_close_paren = header.rfind(')')
    if last_close_paren != -1 and ':' not in header[last_close_paren + 1:]:
        return False
    return True
