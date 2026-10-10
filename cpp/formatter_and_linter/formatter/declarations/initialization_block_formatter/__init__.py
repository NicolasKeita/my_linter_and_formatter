#!/usr/bin/env python3
"""
Initialization Block Formatter

Enforces an empty line after the first block of local variable declarations
at the beginning of a function body.
"""

from .patterns import DECLARATION_PATTERN, _is_class_or_namespace_block, _is_declaration_line
from .scan_state import FormatterState, append_statement_tail, collect_block_comment


def _handle_outside_function(state: FormatterState, lines: list[str], i: int) -> int:
    """Append a line found outside any function and open a new function body
    when the line is the lone '{' of a function signature. Returns next index."""
    line = lines[i]
    state.result.append(line)
    if line.strip() == "{":
        if not _is_class_or_namespace_block(lines, i - 1):
            state.in_function = True
            state.brace_depth = 1
            state.in_init_block = True
            state.has_declarations = False
    return i + 1


def _handle_init_zone(state: FormatterState, lines: list[str], i: int, stripped: str) -> int:
    """Handle one line of the leading initialization block. Returns next index."""
    line = lines[i]
    if not stripped:
        if state.has_declarations:
            state.in_init_block = False
        state.flush_comments()
        state.result.append(line)
        return i + 1

    if _is_declaration_line(stripped):
        state.has_declarations = True
        state.flush_comments()
        state.result.append(line)
        next_index, state.brace_depth = append_statement_tail(
            lines, i, state.brace_depth, state.result
        )
        return next_index

    if state.has_declarations:
        state.result.append("")
    state.in_init_block = False
    state.flush_comments()
    state.result.append(line)
    return i + 1


def _handle_in_function(state: FormatterState, lines: list[str], i: int) -> int:
    """Handle one line inside a function body. Returns the next index."""
    line = lines[i]
    stripped = line.strip()

    if stripped.startswith("//"):
        state.comment_buffer.append(line)
        return i + 1

    if stripped.startswith("/*"):
        collected, next_index = collect_block_comment(lines, i)
        state.comment_buffer.extend(collected)
        return next_index

    state.brace_depth += stripped.count("{")
    state.brace_depth -= stripped.count("}")

    if state.brace_depth == 0:
        state.flush_comments()
        state.in_function = False
        state.in_init_block = False
        state.result.append(line)
        return i + 1

    if not state.in_init_block:
        state.flush_comments()
        state.result.append(line)
        return i + 1

    return _handle_init_zone(state, lines, i, stripped)


def format_initialization_blocks(code: str) -> str:
    """
    Inserts an empty line after the first block of declarations in a function body.
    """
    lines = code.splitlines()
    state = FormatterState()

    i = 0
    while i < len(lines):
        if state.in_function:
            i = _handle_in_function(state, lines, i)
        else:
            i = _handle_outside_function(state, lines, i)

    state.flush_comments()
    return '\n'.join(state.result) + ('\n' if code.endswith('\n') else '')


__all__ = ["format_initialization_blocks", "DECLARATION_PATTERN"]
