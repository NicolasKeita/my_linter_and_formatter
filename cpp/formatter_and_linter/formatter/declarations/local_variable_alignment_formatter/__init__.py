#!/usr/bin/env python3
"""
Local Variable Alignment Formatter

Vertical alignment pass for C++ function bodies. In every function
definition the very first contiguous run of local variable declarations --
the block that starts right after the opening brace '{' -- is reformatted so
that the variable names all begin on the same column, computed from the
longest declaration type of the block plus one separator space. The
initializer that follows the name ('=' value, '{...}', '(args)') stays
attached to the name, so alignment only widens the gap between the type and
the variable name.

Scope rules
-----------
* Only the *first* contiguous declaration block at the top of a function body
  is aligned. A statement that opens a multi-line initializer ('Type name{',
  'Type name(' or 'Type name = make(') is collected as one logical
  declaration: its continuation lines are consumed verbatim until the brace
  depth returns to the statement base and the closing ';' is reached, so a
  wrapped initializer never splits the block in two.
* The first line that is not the start of a variable declaration (control
  structure, function call, reassignment, blank line, comment, ...) ends the
  block, and the rest of the function body is copied verbatim: later
  declaration blocks are left alone.
* Alignment is applied only when the block contains at least two
  declarations; a lone declaration keeps its original spacing.
* The alignment column is computed once from the longest type of the *whole*
  block -- template types like 'std::array<FaultScenario, 1>' included -- so
  every variable name of the block starts at indentation + max type width + 1,
  including the first line of multi-line statements.
* Leading blank lines right after the opening brace are skipped (and
  preserved) so the block can still be found and aligned.
* Base indentation and trailing initializers are preserved; trailing line
  comments are detached, the line is realigned, then the comment is
  re-attached after the rebuilt initializer.

The pass reuses the shared declaration parser (with its constructor-call
'allow_paren_init' mode, which is only legal at function scope) and the same
function-open-brace detection as the declaration blank-line formatter. It is
meant to run after line joining so wrapped declarations are already back on
one line; it is applied to non module-interface files, matching the other
local-declaration passes.
"""

from shared.brace_utils import brace_delta

from formatter.declarations.declaration_blank_line_formatter import is_function_open_brace

from .block import _process_first_block


def align_first_declaration_blocks(code: str) -> str:
    """Align the first contiguous block of local variable declarations at the
    top of every C++ function body found in ``code``."""
    if not code:
        return code
    lines = code.splitlines()
    result: list[str] = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if is_function_open_brace(line, lines, i) and brace_delta(line) > 0:
            result.append(line)
            i = _process_first_block(lines, i + 1, result)
            continue
        result.append(line)
        i += 1
    return "\n".join(result) + ("\n" if code.endswith("\n") else "")


__all__ = ["align_first_declaration_blocks"]
