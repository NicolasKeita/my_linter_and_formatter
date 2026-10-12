#!/usr/bin/env python3
"""Literal scanners: digit separators, raw-string prefixes, literal entry."""

from linter.module.cppm_inline_function_checks.block_model import _SanitizeState


def _is_digit_separator(code: str, index: int) -> bool:
    if index <= 0 or index + 1 >= len(code):
        return False
    previous = code[index - 1]
    following = code[index + 1]
    if not (previous.isdigit() and (following.isalnum() or following == '_')):
        return False
    run_start = index - 1
    while run_start > 0 and code[run_start - 1].isdigit():
        run_start -= 1
    before_run = code[run_start - 1] if run_start > 0 else ''
    return not (before_run.isalpha() or before_run == '_')


def _raw_string_prefix_length(code: str, quote_index: int) -> int:
    if quote_index <= 0 or code[quote_index - 1] != 'R':
        return 0
    r_index = quote_index - 1
    before_r = r_index - 1
    if before_r < 0:
        return 1
    previous = code[before_r]
    if previous in ('u', 'U', 'L'):
        before_prefix = before_r - 1
        if before_prefix < 0 or not (code[before_prefix].isalnum() or code[before_prefix] == '_'):
            return 2
        return 0
    if previous == '8' and before_r - 1 >= 0 and code[before_r - 1] == 'u':
        before_prefix = before_r - 2
        if before_prefix < 0 or not (code[before_prefix].isalnum() or code[before_prefix] == '_'):
            return 3
        return 0
    if previous.isalnum() or previous == '_':
        return 0
    return 1


def _enter_literal(code: str, chars: list[str], quote_index: int) -> tuple[int, _SanitizeState, str]:
    prefix_length = _raw_string_prefix_length(code, quote_index)
    if prefix_length == 0:
        chars[quote_index] = ' '
        return quote_index + 1, _SanitizeState.STRING, ''
    delimiter_end = code.find('(', quote_index + 1, quote_index + 18)
    delimiter = code[quote_index + 1:delimiter_end] if delimiter_end != -1 else ''
    if delimiter_end == -1 or any(char in ' \\()' for char in delimiter):
        chars[quote_index] = ' '
        return quote_index + 1, _SanitizeState.STRING, ''
    for offset in range(quote_index - prefix_length, delimiter_end + 1):
        chars[offset] = ' '
    terminator = ')' + delimiter + '"'
    return delimiter_end + 1, _SanitizeState.RAW_STRING, terminator
