#!/usr/bin/env python3
"""Brace-state scan of sanitised code for over-sized inline function bodies."""

from linter.module.cppm_inline_function_checks.block_model import _Block, _BlockKind
from linter.module.cppm_inline_function_checks.effective_lines import _count_effective_lines
from linter.module.cppm_inline_function_checks.header_classify import (
    _classify_header,
    _compute_line_starts,
    _is_braced_initializer,
    _line_of_position,
    _split_header,
)


def _close_function_block(state: dict, block: _Block, close_index: int) -> None:
    if block.kind != _BlockKind.FUNCTION:
        return
    effective_lines = _count_effective_lines(
        state["sanitized"], state["line_starts"], block.open_pos, close_index
    )
    if effective_lines > state["max_body_lines"]:
        start_line = _line_of_position(state["line_starts"], block.start_pos) + 1
        state["violations"].append((block.name, start_line, effective_lines))


def _open_function_block(sanitized: str, segment_start: int, brace_index: int) -> _Block:
    header = sanitized[segment_start:brace_index]
    significant_header, offset = _split_header(header)
    kind, name = _classify_header(significant_header)
    return _Block(kind, name, brace_index, segment_start + offset, False)


def _handle_open_brace(sanitized: str, segment_start: int, index: int) -> tuple[_Block, int]:
    if _is_braced_initializer(sanitized, segment_start, index):
        return _Block(_BlockKind.OTHER, '', index, index, True), segment_start
    block = _open_function_block(sanitized, segment_start, index)
    return block, index + 1


def _handle_close_brace(state: dict, index: int) -> None:
    blocks = state["blocks"]
    if not blocks:
        state["segment_start"] = index + 1
        return
    block = blocks.pop()
    _close_function_block(state, block, index)
    if not block.transparent:
        state["segment_start"] = index + 1


def _advance(sanitized: str, index: int, char: str, state: dict) -> None:
    if char == '(':
        state["paren_depth"] += 1
    elif char == ')':
        state["paren_depth"] = max(0, state["paren_depth"] - 1)
    elif char == '{' and state["paren_depth"] == 0:
        block, state["segment_start"] = _handle_open_brace(
            sanitized, state["segment_start"], index
        )
        state["blocks"].append(block)
    elif char == '}' and state["paren_depth"] == 0:
        _handle_close_brace(state, index)
    elif char == ';' and state["paren_depth"] == 0:
        state["segment_start"] = index + 1


def _scan_sanitized_code(sanitized: str, max_body_lines: int) -> list[tuple[str, int, int]]:
    line_starts = _compute_line_starts(sanitized)
    state = {
        "sanitized": sanitized,
        "blocks": [],
        "violations": [],
        "segment_start": 0,
        "paren_depth": 0,
        "line_starts": line_starts,
        "max_body_lines": max_body_lines,
    }
    for index in range(len(sanitized)):
        _advance(sanitized, index, sanitized[index], state)
    violations = state["violations"]
    violations.sort(key=lambda violation: violation[1])
    return violations
