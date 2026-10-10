#!/usr/bin/env python3
"""
Using Statement Reordering After Imports

Groups top-level using statements right after the import block that follows
the module declaration.
"""

import re

from shared.regex_patterns import (
    IMPORT_REGEX,
    MODULE_DECL_REGEX,
    MODULE_PARTITION_REGEX,
    USING_REGEX,
)


def _collect_using_group(lines: list[str], i: int) -> tuple[list[str], list[str], list[str], int]:
    """Collect the contiguous import / using / blank-line group starting at
    ``lines[i]``; returns (imports, usings, trailing_blanks, next_index)."""
    imports_list: list[str] = []
    usings: list[str] = []
    trailing_blank_lines: list[str] = []

    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()

        if re.match(IMPORT_REGEX, current_line):
            imports_list.append(current_line)
            i += 1
        elif re.match(USING_REGEX, current_line):
            usings.append(current_line)
            i += 1
        elif current_stripped == '':
            trailing_blank_lines.append(current_line)
            i += 1
        else:
            break

    return imports_list, usings, trailing_blank_lines, i


def _starts_using_group(line: str, new_lines: list[str]) -> bool:
    """Tell whether ``line`` opens an import/using group: it is an import, or a
    using that follows a blank line, an import, a using or a module declaration."""
    if re.match(IMPORT_REGEX, line):
        return True
    if not re.match(USING_REGEX, line):
        return False
    if not new_lines or new_lines[-1].strip() == '':
        return True
    return bool(
        re.match(MODULE_DECL_REGEX, new_lines[-1])
        or re.match(MODULE_PARTITION_REGEX, new_lines[-1])
        or re.match(IMPORT_REGEX, new_lines[-1])
        or re.match(USING_REGEX, new_lines[-1])
    )


def reorder_using_after_import(code: str) -> str:
    lines = code.splitlines()
    new_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if re.match(MODULE_DECL_REGEX, line) or re.match(MODULE_PARTITION_REGEX, line):
            new_lines.append(line)
            i += 1
            continue

        if not _starts_using_group(line, new_lines):
            new_lines.append(line)
            i += 1
            continue

        imports_list, usings, trailing_blank_lines, i = _collect_using_group(lines, i)
        new_lines.extend(imports_list)
        new_lines.extend(usings)

        if i < len(lines) and lines[i].strip() != '':
            if trailing_blank_lines or (new_lines and new_lines[-1].strip() != ''):
                new_lines.append('')

    return '\n'.join(new_lines)
