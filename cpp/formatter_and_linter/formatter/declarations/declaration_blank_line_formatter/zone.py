#!/usr/bin/env python3
"""Walk of the leading declaration zone of a C++ function body."""

from shared.brace_utils import brace_delta

from formatter.declarations.initialization_block_formatter import DECLARATION_PATTERN


def _statement_end(stripped: str, depth: int) -> bool:
    return depth <= 1 and (stripped.endswith(';') or stripped.endswith('}'))


def _flush_and_stop(lines: list[str], i: int, pending: list[str], result: list[str]) -> int:
    """Emit the pending blank lines plus ``lines[i]`` and stop the zone walk;
    returns the index at which normal scanning resumes."""
    result.extend(pending)
    result.append(lines[i])
    return i + 1


def _copy_block_comment(lines: list[str], i: int, result: list[str]) -> int:
    """Copy the lines following ``lines[i]`` until the block comment closes;
    returns the index at which normal scanning resumes."""
    n = len(lines)
    j = i
    while j + 1 < n and '*/' not in lines[j]:
        j += 1
        result.append(lines[j])
    return j + 1


def _consume_continuation(lines: list[str], i: int, brace_depth: int, result: list[str]) -> tuple[int, int]:
    """Copy the continuation lines of a multi-line declaration until the
    statement ends; returns the next index and the new brace depth."""
    n = len(lines)
    while i < n:
        current = lines[i]
        stripped = current.strip()
        delta = brace_delta(current)
        result.append(current)
        brace_depth += delta
        i += 1
        if _statement_end(stripped, brace_depth) or brace_depth <= 0:
            break
    return i, brace_depth


def _consume_declaration(
    lines: list[str],
    i: int,
    brace_depth: int,
    result: list[str],
) -> tuple[int, int]:
    """Emit the declaration line ``lines[i]`` and its continuation lines;
    returns the next index and the new brace depth."""
    line = lines[i]
    stripped = line.strip()
    brace_depth += brace_delta(line)
    result.append(line)
    i += 1
    if not _statement_end(stripped, brace_depth):
        i, brace_depth = _consume_continuation(lines, i, brace_depth, result)
    return i, brace_depth


def _process_declaration_zone(lines: list[str], start: int, result: list[str]) -> int:
    """
    Walk the leading declaration zone of a function body starting at ``start``,
    appending to ``result`` and returning the index at which normal scanning
    should resume.
    """
    n = len(lines)
    i = start
    brace_depth = 1
    pending: list[str] = []
    has_seen_declaration = False

    while i < n:
        line = lines[i]
        stripped = line.strip()
        delta = brace_delta(line)

        if brace_depth + delta <= 0:
            return _flush_and_stop(lines, i, pending, result)

        if not stripped:
            pending.append(line)
            i += 1
            continue

        if stripped.startswith('/*'):
            _flush_and_stop(lines, i, pending, result)
            return _copy_block_comment(lines, i, result)

        if stripped.startswith('//') or not DECLARATION_PATTERN.match(stripped):
            return _flush_and_stop(lines, i, pending, result)

        if not has_seen_declaration:
            result.extend(pending)
        pending = []
        has_seen_declaration = True
        i, brace_depth = _consume_declaration(lines, i, brace_depth, result)

    return i
