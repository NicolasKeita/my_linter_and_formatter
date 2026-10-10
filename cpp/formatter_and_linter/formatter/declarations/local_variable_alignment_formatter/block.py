#!/usr/bin/env python3
"""Collection, alignment and emission of a function's first declaration block."""

from shared.brace_utils import brace_delta

from .collect import _collect_statement
from .statement import StatementBlock


def _flush_block(block: list[StatementBlock], result: list[str]) -> None:
    """Emit the collected first-block statements: aligned on one column when
    the block has at least two of them, otherwise verbatim and untouched."""
    if len(block) < 2:
        for statement in block:
            result.append(statement.original_line)
            result.extend(statement.continuation)
        block.clear()
        return
    target = max(len(statement.parts.type_part) for statement in block) + 1
    for statement in block:
        parts = statement.parts
        rebuilt = (
            parts.indent
            + parts.type_part
            + " " * (target - len(parts.type_part))
            + parts.name
            + statement.tail
        )
        if parts.comment:
            rebuilt = rebuilt.rstrip() + " " + parts.comment
        result.append(rebuilt)
        result.extend(statement.continuation)
    block.clear()


def _copy_until_close(lines: list[str], start: int, result: list[str], brace_depth: int) -> int:
    """Copy lines verbatim from ``start`` until the function's closing brace
    brings ``brace_depth`` back to zero. Returns the index past that brace."""
    n = len(lines)
    i = start
    while i < n:
        line = lines[i]
        brace_depth += brace_delta(line)
        result.append(line)
        if brace_depth <= 0:
            return i + 1
        i += 1
    return i


def _stop_at_non_declaration(
    lines: list[str],
    i: int,
    resume: tuple[int, int],
    block: list[StatementBlock],
    result: list[str],
) -> int:
    """End the aligned block on a non-declaration statement and copy the rest
    of the function body verbatim. ``resume`` carries the next index and the
    brace depth to continue with. Returns the index to resume at."""
    _flush_block(block, result)
    next_index, depth = resume
    result.extend(lines[i:next_index])
    if depth <= 0:
        return next_index
    return _copy_until_close(lines, next_index, result, depth)


def _process_first_block(lines: list[str], start: int, result: list[str]) -> int:
    """Align the first contiguous declaration block of the function body whose
    first line is ``lines[start]``. Returns the index to resume scanning at."""
    n = len(lines)
    i = start
    brace_depth = 1
    block: list[StatementBlock] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()
        delta = brace_delta(line)

        if brace_depth + delta <= 0:
            _flush_block(block, result)
            result.append(line)
            return i + 1

        if not block and not stripped:
            result.append(line)
            brace_depth += delta
            i += 1
            continue

        statement, next_index, new_depth = _collect_statement(lines, i, brace_depth)
        if statement is None and next_index == i:
            _flush_block(block, result)
            result.append(line)
            return _copy_until_close(lines, i + 1, result, brace_depth + delta)
        if statement is None:
            return _stop_at_non_declaration(
                lines, i, (next_index, new_depth), block, result
            )

        block.append(statement)
        brace_depth = new_depth
        i = next_index

    _flush_block(block, result)
    return i
