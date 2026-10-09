#!/usr/bin/env python3
"""
Include formatting utilities for the C++ code formatter.

Organizes #include statements: system vs local separation, duplicate removal,
and proper spacing.
"""

import re

from shared.regex_patterns import FUNC_REGEX, INCLUDE_REGEX


def extract_includes(code_lines: list[str]) -> tuple[list[str], list[str]]:
    include_lines = []
    other_lines = []
    for line in code_lines:
        if re.match(INCLUDE_REGEX, line):
            include_lines.append(line.strip())
        else:
            other_lines.append(line)
    return include_lines, other_lines


def remove_duplicate_includes(includes: list[str]) -> list[str]:
    seen = set()
    unique = []
    for inc in includes:
        content = re.match(INCLUDE_REGEX, inc).group(1)
        if content not in seen:
            seen.add(content)
            unique.append(inc)
    return unique


def separate_system_local(includes: list[str]) -> tuple[list[str], list[str]]:
    windows_h_include = None
    system_includes = []
    local_includes = []

    for inc in includes:
        content = re.match(INCLUDE_REGEX, inc).group(1)
        if content == '<windows.h>':
            windows_h_include = inc
        elif content.startswith('<'):
            system_includes.append(inc)
        else:
            local_includes.append(inc)

    system_includes.sort()
    if windows_h_include:
        system_includes.insert(0, windows_h_include)

    return system_includes, local_includes


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


def format_include_group(include_lines: list[str]) -> list[str]:
    include_lines = remove_duplicate_includes(include_lines)
    system_includes, local_includes = separate_system_local(include_lines)
    local_includes.sort()
    formatted_includes = system_includes.copy()
    if system_includes and local_includes:
        formatted_includes.append('')
    formatted_includes.extend(local_includes)
    return formatted_includes


def format_includes(code: str) -> str:
    lines = code.splitlines()
    lines = remove_blank_lines_between_includes(lines)

    new_lines: list[str] = []
    pending_group: list[str] = []
    seen_contents: set[str] = set()

    def flush_pending_group() -> None:
        if pending_group:
            new_lines.extend(format_include_group(pending_group))
            pending_group.clear()

    for line in lines:
        include_match = re.match(INCLUDE_REGEX, line)
        if include_match:
            content = include_match.group(1)
            if content not in seen_contents:
                seen_contents.add(content)
                pending_group.append(line)
        else:
            flush_pending_group()
            if re.match(r'^\s*#', line):
                seen_contents.clear()
            new_lines.append(line)

    flush_pending_group()
    lines = new_lines

    lines = ensure_single_blank_lines(lines)
    return '\n'.join(lines)