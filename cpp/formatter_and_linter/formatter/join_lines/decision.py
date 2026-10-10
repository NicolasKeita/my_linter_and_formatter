#!/usr/bin/env python3
"""Per-pair decision logic: whether two consecutive lines may be merged."""

from shared.function_analysis import has_stream_operators

from .patterns import (
    _ACCESS_SPECIFIER,
    _CASE_LABEL,
    _CONTROL_HEADER,
    _CONTROL_HEADER_LINE,
    _LABEL,
    _OPEN_BRACE_HEADER,
    _TYPE_HEADER,
    _UNARY_START,
)
from .triggers import (
    _ends_with_trigger,
    _has_line_comment,
    _starts_with_trigger,
)


def _is_protected_pair(n: str, m: str, n_protected: bool, m_protected: bool) -> bool:
    """Return True when a pair of lines must never be merged for static reasons."""
    if not n or not m:
        return True
    if n_protected or m_protected:
        return True
    if n.lstrip().startswith("#") or m.startswith("#"):
        return True
    if _has_line_comment(n) or _has_line_comment(m):
        return True
    if m.startswith("[["):
        return True
    if n.endswith((";", "}")):
        return True
    if has_stream_operators(n):
        return True
    if m.startswith("<<") or m.startswith(">>"):
        return True
    return bool(_ACCESS_SPECIFIER.match(n) or _CASE_LABEL.match(n) or _LABEL.match(n))


def _join_onto_brace(n: str, m: str, ends: bool) -> bool:
    """Decide a merge when the next line starts with an opening/closing brace."""
    if m.startswith("{"):
        if ends:
            return True
        return bool(_CONTROL_HEADER.match(n))
    if not ends:
        return False
    if n.strip() == "{":
        return False
    return True


def _join_by_trigger(n: str, m: str, ends: bool) -> bool:
    """Decide a merge based on continuation triggers when no brace is involved."""
    if ends:
        if n.endswith("{"):
            if n.strip() == "{" or _OPEN_BRACE_HEADER.search(n) or _TYPE_HEADER.match(n):
                return False
        return True
    if not _starts_with_trigger(m):
        return False
    if _CONTROL_HEADER_LINE.match(n) and m[0] in _UNARY_START:
        return False
    return True


def _can_join_line(line_n: str, line_next: str, n_protected: bool, m_protected: bool, max_length: int) -> bool:
    n = line_n.rstrip()
    m = line_next.strip()

    if _is_protected_pair(n, m, n_protected, m_protected):
        return False
    if len(n) + 1 + len(m) > max_length:
        return False

    ends = _ends_with_trigger(n)

    if m.startswith("{") or m.startswith("}"):
        return _join_onto_brace(n, m, ends)

    return _join_by_trigger(n, m, ends)
