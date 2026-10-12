#!/usr/bin/env python3
"""Comment and literal sanitisation for the cppm inline function scanner."""

from linter.module.cppm_inline_function_checks.block_model import _SanitizeState
from linter.module.cppm_inline_function_checks.literal_scanners import (
    _enter_literal,
    _is_digit_separator,
)


def _sanitize_code_state(chars: list[str], code: str, index: int, state: _SanitizeState) -> tuple:
    char = code[index]
    following = code[index + 1] if index + 1 < len(code) else ''
    if char == '/' and following == '/':
        chars[index] = ' '
        chars[index + 1] = ' '
        return index + 2, _SanitizeState.LINE_COMMENT, ''
    if char == '/' and following == '*':
        chars[index] = ' '
        chars[index + 1] = ' '
        return index + 2, _SanitizeState.BLOCK_COMMENT, ''
    if char == '"':
        index, state, raw_terminator = _enter_literal(code, chars, index)
        return index, state, raw_terminator
    if char == "'":
        if _is_digit_separator(code, index):
            return index + 1, _SanitizeState.CODE, ''
        chars[index] = ' '
        return index + 1, _SanitizeState.CHAR, ''
    return index + 1, _SanitizeState.CODE, ''


def _sanitize_line_comment(chars: list[str], char: str, index: int) -> tuple[int, _SanitizeState]:
    if char == '\n':
        return index + 1, _SanitizeState.CODE
    chars[index] = ' '
    return index + 1, _SanitizeState.LINE_COMMENT


def _sanitize_block_comment(chars: list[str], code: str, char: str, following: str, index: int) -> tuple:
    if char == '*' and following == '/':
        chars[index] = ' '
        chars[index + 1] = ' '
        return index + 2, _SanitizeState.CODE
    if char != '\n':
        chars[index] = ' '
    return index + 1, _SanitizeState.BLOCK_COMMENT


def _sanitize_quote_state(chars: list[str], char: str, following: str, index: int, state: _SanitizeState) -> tuple:
    quote = '"' if state == _SanitizeState.STRING else "'"
    if char == '\\':
        chars[index] = ' '
        if following and following != '\n':
            chars[index + 1] = ' '
            return index + 2, state
        return index + 1, state
    if char == quote:
        chars[index] = ' '
        return index + 1, _SanitizeState.CODE
    if char == '\n':
        return index + 1, _SanitizeState.CODE
    chars[index] = ' '
    return index + 1, state


def _sanitize_string_or_char(chars: list[str], char: str, following: str, index: int, state: _SanitizeState) -> tuple:
    return _sanitize_quote_state(chars, char, following, index, state)


def _sanitize_raw_string(chars: list[str], code: str, char: str, index: int, raw_terminator: str) -> tuple:
    if code.startswith(raw_terminator, index):
        for offset in range(index, index + len(raw_terminator)):
            chars[offset] = ' '
        index += len(raw_terminator)
        return index, _SanitizeState.CODE
    if char != '\n':
        chars[index] = ' '
    return index + 1, _SanitizeState.RAW_STRING


def _dispatch_sanitizer(chars: list[str], code: str, index: int, state: _SanitizeState, raw_terminator: str) -> tuple:
    char = code[index]
    following = code[index + 1] if index + 1 < len(code) else ''

    if state == _SanitizeState.CODE:
        index, state, raw_terminator = _sanitize_code_state(chars, code, index, state)
    elif state == _SanitizeState.LINE_COMMENT:
        index, state = _sanitize_line_comment(chars, char, index)
    elif state == _SanitizeState.BLOCK_COMMENT:
        index, state = _sanitize_block_comment(chars, code, char, following, index)
    elif state in (_SanitizeState.STRING, _SanitizeState.CHAR):
        index, state = _sanitize_string_or_char(chars, char, following, index, state)
    elif state == _SanitizeState.RAW_STRING:
        index, state = _sanitize_raw_string(chars, code, char, index, raw_terminator)

    return index, state, raw_terminator


def _sanitize_code(code: str) -> str:
    chars = list(code)
    length = len(code)
    state = _SanitizeState.CODE
    raw_terminator = ''
    index = 0
    while index < length:
        index, state, raw_terminator = _dispatch_sanitizer(
            chars, code, index, state, raw_terminator
        )
    return ''.join(chars)
