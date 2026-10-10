#!/usr/bin/env python3
"""Statement-level protected masks: enums, initializer lists, oversized blocks."""

from .patterns import _ENUM_START
from .triggers import _is_statement_continuation


def _enum_mask(lines: list[str]) -> list[bool]:
    """
    Mark every line of an enum declaration, from the 'enum' keyword up to the
    closing '};', so those lines are never joined.
    """
    mask = [False] * len(lines)
    total = len(lines)
    i = 0
    while i < total:
        if not _ENUM_START.match(lines[i]):
            i += 1
            continue
        j = i
        depth = 0
        seen_open = False
        while j < total:
            if not seen_open and j > i:
                if not lines[j].lstrip().startswith("{"):
                    break
            mask[j] = True
            opens = lines[j].count("{")
            closes = lines[j].count("}")
            if not seen_open:
                if opens:
                    seen_open = True
                    depth = opens - closes
            else:
                depth += opens - closes
            if seen_open and depth <= 0:
                break
            j += 1
        i = j + 1
    return mask


def _init_list_mask(lines: list[str]) -> list[bool]:
    """
    Mark every line of a constructor member initializer list (the lines
    starting with ':' or ',' that follow a constructor signature ending with
    ')'), so those lines are never joined together or onto the signature.
    """
    mask = [False] * len(lines)
    total = len(lines)
    i = 0
    while i < total:
        if not lines[i].lstrip().startswith(":"):
            i += 1
            continue
        prev = i - 1
        while prev >= 0 and not lines[prev].strip():
            prev -= 1
        if prev < 0 or not lines[prev].rstrip().endswith(")"):
            i += 1
            continue
        j = i
        while j < total:
            mask[j] = True
            if not lines[j].rstrip().endswith(","):
                break
            j += 1
        i = j + 1
    return mask


def _oversized_statement_mask(
    lines: list[str],
    max_length: int,
    protected_base: list[bool],
    stream_mask: list[bool],
) -> list[bool]:
    """
    Mark every line of a multi-line statement whose fully-joined length exceeds
    max_length (e.g. a std::array '{{ ... }}' block or a long call). Such
    statements are left completely untouched: neither the individual lines nor
    partial prefixes are joined. Statements that fit within max_length when
    joined are left free so the usual per-line merging applies.
    """
    mask = [False] * len(lines)
    total = len(lines)
    i = 0
    while i < total:
        if protected_base[i] or stream_mask[i]:
            i += 1
            continue
        j = i
        while j + 1 < total and not protected_base[j + 1] and not stream_mask[j + 1]:
            if not _is_statement_continuation(lines[j], lines[j + 1]):
                break
            j += 1
        if j > i:
            joined = lines[i].rstrip()
            for k in range(i + 1, j + 1):
                joined += " " + lines[k].strip()
            if len(joined) > max_length:
                for k in range(i, j + 1):
                    mask[k] = True
        i = j + 1
    return mask
