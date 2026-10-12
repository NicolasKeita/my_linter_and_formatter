#!/usr/bin/env python3
"""Parse the 'module <Name>;' declaration from a C++20 unit file."""

import re

_MODULE_DECLARATION_PATTERN = re.compile(r"^\s*module\s+([A-Za-z_]\w*)\s*;")


def _match_declaration(text: str) -> str | None:
    match = _MODULE_DECLARATION_PATTERN.match(text)
    return match.group(1) if match else None


def declared_module(file_path: str) -> str | None:
    """
    Return the name declared by a 'module <Name>;' unit in the file, or None.

    Comment blocks are skipped so that a 'module' word appearing inside the
    header description is not mistaken for a module declaration.
    """
    try:
        with open(file_path, encoding="utf-8", errors="replace") as handle:
            in_block_comment = False
            for line in handle:
                stripped = line
                if in_block_comment:
                    end_index = stripped.find("*/")
                    if end_index == -1:
                        continue
                    stripped = stripped[end_index + len("*/"):]
                    in_block_comment = False
                start_index = stripped.find("/*")
                if start_index != -1:
                    head = stripped[:start_index]
                    name = _match_declaration(head)
                    if name:
                        return name
                    end_index = stripped.find("*/", start_index + len("/*"))
                    if end_index == -1:
                        in_block_comment = True
                        continue
                    stripped = stripped[end_index + len("*/"):]
                name = _match_declaration(stripped)
                if name:
                    return name
    except (OSError, ValueError):
        return None
    return None
