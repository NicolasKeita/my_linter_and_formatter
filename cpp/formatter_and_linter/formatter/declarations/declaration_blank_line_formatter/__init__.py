#!/usr/bin/env python3
"""
Declaration Blank-Line Formatter

Removes the blank lines that separate consecutive local variable declarations at
the very beginning of a C++ function body, packing the declaration block together.

Rules implemented
-----------------
* The "declaration zone" starts immediately after the opening brace ``{`` of a
  function definition, whether that brace sits on the signature line
  (``void f() {``) or on its own line (``void f()\\n{``).
* Inside the zone, every blank line located *between* two consecutive
  declaration statements is removed.
* The declaration forms recognised are the ones covered by the shared
  ``DECLARATION_PATTERN`` (basic declarations, assignments, uniform/aggregate
  initialisers and templates with a constructor call).
* The first line that is not a declaration (control structure, function call,
  reassignment, ...) ends the zone and is left untouched.  Blank lines that
  follow the last declaration -- the separator between the declaration block
  and the rest of the body -- are preserved as-is.

This formatter is the complement of ``format_initialization_blocks``: the
latter guarantees one blank line *after* the declaration block, this one
removes the blank lines *between* the declarations.
"""

from shared.brace_utils import brace_delta

from .function_brace import is_function_open_brace
from .zone import _process_declaration_zone


def remove_blank_lines_between_declarations(code: str) -> str:
    """
    Remove blank lines located between consecutive variable declarations at the
    beginning of every C++ function body found in ``code``.
    """
    lines = code.splitlines()
    result: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if is_function_open_brace(line, lines, i):
            if brace_delta(line) <= 0:
                result.append(line)
                i += 1
                continue
            result.append(line)
            i = _process_declaration_zone(lines, i + 1, result)
            continue
        result.append(line)
        i += 1

    return '\n'.join(result) + ('\n' if code.endswith('\n') else '')


__all__ = ["remove_blank_lines_between_declarations", "is_function_open_brace"]
