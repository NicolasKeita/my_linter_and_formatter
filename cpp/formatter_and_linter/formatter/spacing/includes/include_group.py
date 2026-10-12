#!/usr/bin/env python3
"""
Include Grouping Helpers

Deduplication, system/local separation and ordering of #include statements.
"""

import re

from shared.regex_patterns import INCLUDE_REGEX


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


def format_include_group(include_lines: list[str]) -> list[str]:
    include_lines = remove_duplicate_includes(include_lines)
    system_includes, local_includes = separate_system_local(include_lines)
    local_includes.sort()
    formatted_includes = system_includes.copy()
    if system_includes and local_includes:
        formatted_includes.append('')
    formatted_includes.extend(local_includes)
    return formatted_includes
