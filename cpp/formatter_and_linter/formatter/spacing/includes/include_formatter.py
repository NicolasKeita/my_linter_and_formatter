#!/usr/bin/env python3
"""
Include formatting utilities for the C++ code formatter.

Organizes #include statements: system vs local separation, duplicate removal,
and proper spacing.
"""

import re

from formatter.spacing.includes.include_blank_lines import (
    ensure_single_blank_lines,
    remove_blank_lines_between_includes,
)
from formatter.spacing.includes.include_group import format_include_group
from shared.regex_patterns import INCLUDE_REGEX


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
