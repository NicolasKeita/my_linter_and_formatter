#!/usr/bin/env python3
"""Mask for multi-operator '&&' / '||' logical chains."""

from .triggers import (
    _count_logical_operators,
    _ends_logical_chain,
    _ends_with_trigger,
    _starts_logical_chain,
)


def _logical_chain_mask(lines: list[str]) -> list[bool]:
    """
    Mark every line belonging to a '&&' / '||' chain that holds more than one
    operator. A single operator may be joined back onto one line; a
    multi-condition chain keeps each condition on its own line.
    """
    mask = [False] * len(lines)
    counts = [_count_logical_operators(line) for line in lines]
    total = len(lines)
    i = 0
    while i < total:
        if not _starts_logical_chain(lines[i]) and not _ends_logical_chain(lines[i]):
            i += 1
            continue
        j = i
        chain_sum = 0
        while j < total and (
            j == i
            or _starts_logical_chain(lines[j])
            or _ends_logical_chain(lines[j - 1])
        ):
            chain_sum += counts[j]
            j += 1
        if chain_sum > 1:
            start = i
            while start > 0:
                above = lines[start - 1].rstrip()
                if not above:
                    break
                if _starts_logical_chain(lines[start]) or _ends_with_trigger(above):
                    start -= 1
                else:
                    break
            for k in range(start, j):
                mask[k] = True
        i = j
    return mask
