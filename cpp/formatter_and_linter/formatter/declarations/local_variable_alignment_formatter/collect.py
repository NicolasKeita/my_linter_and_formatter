#!/usr/bin/env python3
"""Collection of a full (possibly multi-line) declaration statement."""

from shared.brace_utils import brace_delta
from shared.declaration_parse import DeclarationParts

from .statement import StatementBlock, _parse_local_declaration, _parse_statement_start


def _collect_multiline(
    lines: list[str],
    start: int,
    brace_depth: int,
    statement_start: tuple[DeclarationParts, str],
) -> tuple[StatementBlock | None, int, int]:
    """Consume a multi-line declaration statement whose first line at
    ``lines[start]`` opens a brace or parenthesis initializer.

    Continuation lines are appended verbatim until the brace depth returns to
    the statement base on a line ending with ';'. Returns the statement (or
    None when the statement could not be closed), the next index and the new
    brace depth.
    """
    parts, tail = statement_start
    first_line = lines[start]
    depth = brace_depth + brace_delta(first_line)
    continuation: list[str] = []
    i = start + 1
    n = len(lines)
    while i < n:
        current = lines[i]
        depth += brace_delta(current)
        continuation.append(current)
        i += 1
        if depth <= 0:
            break
        if depth == brace_depth and current.strip().endswith(";"):
            return StatementBlock(parts, tail, tuple(continuation), first_line), i, depth
    return None, i, depth


def _collect_statement(
    lines: list[str],
    start: int,
    brace_depth: int,
) -> tuple[StatementBlock | None, int, int]:
    """Collect one full statement (possibly spanning several lines) starting
    at ``lines[start]`` while the enclosing function body sits at
    ``brace_depth``.

    Returns ``(statement, next_index, new_depth)``. ``statement`` is None when
    the line is not the start of a variable declaration; ``next_index`` then
    points at the first unconsumed line (equal to ``start`` when nothing was
    consumed, or past a multi-line statement that could not be classified and
    must be copied verbatim). A statement ends on the line that brings the
    brace depth back to the statement base and ends with ';'.
    """
    line = lines[start]
    stripped = line.strip()
    if not stripped:
        return None, start, brace_depth
    depth = brace_depth + brace_delta(line)
    if depth == brace_depth and stripped.endswith(";"):
        parsed = _parse_local_declaration(line)
        if parsed is None:
            return None, start, brace_depth
        return StatementBlock(parsed, parsed.rest, (), line), start + 1, depth
    statement_start = _parse_statement_start(line)
    if statement_start is None:
        return None, start, brace_depth
    return _collect_multiline(lines, start, brace_depth, statement_start)
