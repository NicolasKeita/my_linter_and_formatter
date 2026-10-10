#!/usr/bin/env python3
"""Multi-pass join driver: reflow wrapped C++ statements until stable."""

from shared.function_analysis import has_stream_operators

from .decision import _can_join_line
from .logical_mask import _logical_chain_mask
from .masks import (
    _block_comment_mask,
    _signature_mask,
)
from .statement_masks import (
    _enum_mask,
    _init_list_mask,
    _oversized_statement_mask,
)


def _protected_masks(lines: list[str], max_length: int) -> list[bool]:
    """Combine every per-line protection mask into a single protected-line mask."""
    block_mask = _block_comment_mask(lines)
    signature_mask = _signature_mask(lines)
    logical_mask = _logical_chain_mask(lines)
    enum_mask = _enum_mask(lines)
    init_list_mask = _init_list_mask(lines)
    protected_base_mask = [
        block_mask[i] or signature_mask[i] or logical_mask[i] or enum_mask[i] or init_list_mask[i]
        for i in range(len(lines))
    ]
    stream_mask = [has_stream_operators(line) for line in lines]
    oversized_mask = _oversized_statement_mask(lines, max_length, protected_base_mask, stream_mask)
    return [
        protected_base_mask[i] or stream_mask[i] or oversized_mask[i]
        for i in range(len(lines))
    ]


def _join_lines_pass(lines: list[str], max_length: int) -> list[str]:
    protected = _protected_masks(lines, max_length)
    result: list[str] = []
    i = 0
    total = len(lines)
    while i < total:
        n_protected = protected[i]
        m_protected = i + 1 < total and protected[i + 1]
        if (
            i + 1 < total
            and _can_join_line(lines[i], lines[i + 1], n_protected, m_protected, max_length)
        ):
            result.append(lines[i].rstrip() + " " + lines[i + 1].strip())
            i += 2
        else:
            result.append(lines[i])
            i += 1
    return result


def join_lines(code: str, max_length: int = 120) -> str:
    """Merge consecutive C++ lines that fit on a single line of max_length."""
    if not code:
        return code

    lines = code.splitlines()
    while True:
        merged_lines = _join_lines_pass(lines, max_length)
        if merged_lines == lines:
            break
        lines = merged_lines

    joined = "\n".join(lines)
    if code.endswith("\n"):
        joined += "\n"
    return joined


__all__ = ["join_lines"]

