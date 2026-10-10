#!/usr/bin/env python3
"""Protected-line masks: regions that the join pass must never merge."""

from shared.brace_utils import CONTROL_KEYWORDS

from .patterns import (
    _FUNC_DEF_START,
    _QUALIFIED_SIG_START,
)


def _scan_block_comment_line(line: str, in_block: bool) -> tuple[bool, bool]:
    """Scan one line, returning (line_is_masked, still_in_block_afterwards)."""
    line_masked = in_block
    in_string = False
    string_char = ""
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        if in_block:
            if char == "*" and i + 1 < length and line[i + 1] == "/":
                in_block = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if char == "\\":
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue
        if char == "/" and i + 1 < length and line[i + 1] == "/":
            break
        if char == "/" and i + 1 < length and line[i + 1] == "*":
            in_block = True
            line_masked = True
            i += 2
            continue
        i += 1
    return line_masked, in_block


def _block_comment_mask(lines: list[str]) -> list[bool]:
    mask = []
    in_block = False
    for line in lines:
        line_masked, in_block = _scan_block_comment_line(line, in_block)
        mask.append(line_masked)
    return mask


def _mask_balanced_parens(lines: list[str], mask: list[bool], i: int, total: int) -> int:
    """Mask an open-paren signature block starting at line ``i``; return next index."""
    depth = lines[i].count("(") - lines[i].count(")")
    while i < total and depth > 0:
        mask[i] = True
        i += 1
        if i < total:
            depth += lines[i].count("(") - lines[i].count(")")
    if i < total:
        mask[i] = True
    return i + 1


def _signature_mask(lines: list[str]) -> list[bool]:
    """
    Return a mask marking every line belonging to a multi-line function
    signature (definition or prototype). Such lines are never joined, so the
    aligned parameters produced by the parameter formatter are preserved.
    """
    mask = [False] * len(lines)
    total = len(lines)
    i = 0
    while i < total:
        match = _FUNC_DEF_START.match(lines[i])
        name = match.group(1).split("::")[-1] if match else ""
        depth = lines[i].count("(") - lines[i].count(")")
        if match and name not in CONTROL_KEYWORDS and depth > 0:
            i = _mask_balanced_parens(lines, mask, i, total)
            continue
        if _QUALIFIED_SIG_START.match(lines[i]) and depth > 0:
            i = _mask_balanced_parens(lines, mask, i, total)
            continue
        i += 1
    return mask
