#!/usr/bin/env python3
"""
Import Block Spacing Helpers

Blank-line normalization helpers for module declarations and import blocks.
"""

import re

from shared.regex_patterns import (
    IMPORT_REGEX,
    MODULE_DECL_REGEX,
    MODULE_PARTITION_REGEX,
)


def is_module_boundary(line: str) -> bool:
    return bool(re.match(MODULE_DECL_REGEX, line) or re.match(MODULE_PARTITION_REGEX, line))


def handle_module_declaration(lines: list[str], i: int, new_lines: list[str]) -> int:
    """Emit a module declaration, collapse following blanks, then aerate the body."""
    new_lines.append(lines[i])
    i += 1
    while i < len(lines) and lines[i].strip() == '':
        i += 1
    if i < len(lines) and lines[i].strip() != '':
        new_lines.append('')
    return i


def collect_import_block(lines: list[str], i: int) -> tuple[list[str], int]:
    imports: list[str] = []
    while i < len(lines) and re.match(IMPORT_REGEX, lines[i]):
        imports.append(lines[i])
        i += 1
    return imports, i


def needs_blank_before_import(new_lines: list[str]) -> bool:
    if not new_lines:
        return False
    last_line = new_lines[-1]
    if is_module_boundary(last_line):
        return False
    return last_line.strip() != ''


def handle_import_block(lines: list[str], i: int, new_lines: list[str]) -> int:
    """Emit a run of imports with correct surrounding blank-line spacing."""
    imports, i = collect_import_block(lines, i)

    if needs_blank_before_import(new_lines):
        new_lines.append('')
    new_lines.extend(imports)

    while i < len(lines) and lines[i].strip() == '':
        i += 1

    if i < len(lines) and lines[i].strip() != '':
        next_line = lines[i]
        if not re.match(IMPORT_REGEX, next_line) and not is_module_boundary(next_line):
            new_lines.append('')
    return i
