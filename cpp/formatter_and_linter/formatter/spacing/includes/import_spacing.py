#!/usr/bin/env python3
"""
Import Order and Spacing

Sorts import statements (system before project) and normalizes blank-line
spacing around module declarations and import blocks.
"""

import re

from formatter.spacing.includes.import_blocks import (
    handle_import_block,
    handle_module_declaration,
    is_module_boundary,
)
from shared.import_utils import sort_imports
from shared.regex_patterns import IMPORT_REGEX


def format_import_order(code: str) -> str:
    lines = code.splitlines()
    new_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if re.match(IMPORT_REGEX, line):
            imports = []
            while i < len(lines):
                current_line = lines[i]
                current_stripped = current_line.strip()
                if re.match(IMPORT_REGEX, current_line):
                    imports.append(current_line)
                    i += 1
                elif current_stripped == '':
                    i += 1
                else:
                    break

            system_imports, local_imports = sort_imports(imports)

            formatted_imports: list[str] = []
            formatted_imports.extend(system_imports)
            if system_imports and local_imports:
                formatted_imports.append('')
            formatted_imports.extend(local_imports)

            new_lines.extend(formatted_imports)
            continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines)


def format_module_import_spacing(code: str) -> str:
    lines = code.splitlines()
    new_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if is_module_boundary(line):
            i = handle_module_declaration(lines, i, new_lines)
            continue

        if re.match(IMPORT_REGEX, line):
            i = handle_import_block(lines, i, new_lines)
            continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines)
