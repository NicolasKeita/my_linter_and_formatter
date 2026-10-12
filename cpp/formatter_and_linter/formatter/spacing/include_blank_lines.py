#!/usr/bin/env python3
"""
Include Blank-Line Helpers

Blank-line normalization around #include blocks and preprocessor directives.
"""

import re

from shared.regex_patterns import FUNC_REGEX, INCLUDE_REGEX


def ensure_single_blank_lines(lines: list[str]) -> list[str]:
    new_lines = []
    prev_blank = False
    last_was_func_or_comment = False

    for line in lines:
        stripped = line.strip()

        if stripped == '':
            if not prev_blank:
                new_lines.append('')
            prev_blank = True
            last_was_func_or_comment = False
        elif re.match(FUNC_REGEX, line):
            if not prev_blank and new_lines:
                if re.match(FUNC_REGEX, new_lines[-1]):
                    pass
                else:
                    if not last_was_func_or_comment:
                        new_lines.append('')
            new_lines.append(line)
            prev_blank = False
            last_was_func_or_comment = True
        elif stripped.startswith('//') or stripped.startswith('/*'):
            new_lines.append(line)
            prev_blank = False
            last_was_func_or_comment = True
        else:
            new_lines.append(line)
            prev_blank = False
            last_was_func_or_comment = False

    return new_lines


def _blank_line_touches_preprocessor(lines: list[str], blank_index: int) -> bool:
    previous = ''
    for j in range(blank_index - 1, -1, -1):
        if lines[j].strip():
            previous = lines[j].strip()
            break

    following = ''
    for j in range(blank_index + 1, len(lines)):
        if lines[j].strip():
            following = lines[j].strip()
            break

    starts_with_hash = re.compile(r'^\s*#')
    return bool(starts_with_hash.match(previous) or starts_with_hash.match(following))


def remove_blank_lines_between_includes(lines: list[str]) -> list[str]:
    first_include_index = -1
    last_include_index = -1

    for i, line in enumerate(lines):
        if re.match(INCLUDE_REGEX, line):
            if first_include_index == -1:
                first_include_index = i
            last_include_index = i

    if first_include_index == -1:
        return lines

    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i < first_include_index:
            result.append(line)
        elif re.match(INCLUDE_REGEX, line):
            result.append(line)
        elif i > last_include_index:
            if stripped != '' and i == last_include_index + 1:
                if result and result[-1].strip() != '' and not re.match(r'^\s*#', line):
                    result.append('')
            result.append(line)
        elif stripped == '':
            if _blank_line_touches_preprocessor(lines, i):
                result.append(line)
            continue
        else:
            result.append(line)

    return result
