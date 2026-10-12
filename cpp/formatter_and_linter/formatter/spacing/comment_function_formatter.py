#!/usr/bin/env python3
"""
Comment-function spacing formatter for the C++ code formatter.

Handles proper spacing rules where comments above functions have no blank line,
while other code elements maintain proper separation.
"""

import re

from shared.regex_patterns import FUNC_REGEX


def _is_comment_line(text: str) -> bool:
    return text.startswith("//") or text.startswith("/*") or text.endswith("*/")


def _find_last_meaningful(new_lines: list[str]) -> tuple[int, str | None]:
    """Return the index of the last non-blank emitted line and its stripped text."""
    j = len(new_lines) - 1
    while j >= 0 and new_lines[j].strip() == '':
        j -= 1
    if j >= 0:
        return j, new_lines[j].strip()
    return j, None


def _format_function_line(line: str, new_lines: list[str]) -> list[str]:
    """Apply the blank-line rules for a detected function line."""
    j, last_line = _find_last_meaningful(new_lines)

    if last_line is not None and _is_comment_line(last_line):
        while new_lines and new_lines[-1].strip() == '':
            new_lines.pop()
    elif not new_lines or new_lines[-1].strip() != '':
        if last_line is None or not re.match(FUNC_REGEX, new_lines[j]):
            new_lines.append('')

    new_lines.append(line)
    return new_lines


def format_comment_function_spacing(code: str) -> str:
    lines = code.splitlines()
    new_lines: list[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()

        if stripped == '':
            if not prev_blank:
                new_lines.append('')
                prev_blank = True
            continue

        if re.match(FUNC_REGEX, line):
            new_lines = _format_function_line(line, new_lines)
            prev_blank = False
        else:
            new_lines.append(line)
            prev_blank = False

    return '\n'.join(new_lines)
