#!/usr/bin/env python3
"""Blank-line collapsing between consecutive function prototypes."""

from formatter.spacing.prototype_spacing.comment_stripper import strip_comments
from formatter.spacing.prototype_spacing.prototype_detection import (
    apply_braces,
    looks_like_prototype,
    looks_like_prototype_start,
    multiline_signature_ends_as_prototype,
    paren_balance,
)


def _classify_single_line(code: str, state: dict) -> tuple[bool, bool]:
    ends_semi = code.rstrip().endswith(";")
    balance = paren_balance(code)
    has_brace = "{" in code or "}" in code

    if balance == 0 and ends_semi and looks_like_prototype(code):
        return True, True
    if balance > 0 and not ends_semi and not has_brace and looks_like_prototype_start(code):
        state["in_multiline"] = True
        state["balance"] = balance
        flush = multiline_signature_ends_as_prototype(state["stripped"], state["index"])
        return flush, True
    return False, False


def _classify_multiline(code: str, state: dict) -> tuple[bool, bool]:
    state["balance"] += paren_balance(code)
    flush_as_prototype = True
    ends_prototype = True
    if "{" in code or "}" in code:
        state["in_multiline"] = False
        flush_as_prototype = False
    elif state["balance"] <= 0 and code.rstrip().endswith(";"):
        state["in_multiline"] = False
    return flush_as_prototype, ends_prototype


def _flush_pending_blanks(output: list[str], pending_blanks: int, at_namespace_level: bool,
                          prev_ends_prototype: bool, flush_as_prototype: bool) -> None:
    if not (pending_blanks and output):
        return
    if at_namespace_level:
        if not (prev_ends_prototype and flush_as_prototype):
            output.append("")
    else:
        output.extend([""] * pending_blanks)


def collapse_prototype_blank_lines(lines: list[str]) -> list[str]:
    stripped = strip_comments(lines)
    output: list[str] = []
    scope_stack: list[str] = []
    pending_blanks = 0
    prev_ends_prototype = False
    state = {"in_multiline": False, "balance": 0, "stripped": stripped, "index": 0}

    for index, raw in enumerate(lines):
        if raw.strip() == "":
            pending_blanks += 1
            continue

        code = stripped[index]
        at_namespace_level = all(scope == "namespace" for scope in scope_stack)
        state["index"] = index

        if state["in_multiline"]:
            flush_as_prototype, ends_prototype = _classify_multiline(code, state)
        else:
            flush_as_prototype, ends_prototype = _classify_single_line(code, state)

        _flush_pending_blanks(output, pending_blanks, at_namespace_level,
                              prev_ends_prototype, flush_as_prototype)
        pending_blanks = 0

        output.append(raw)
        prev_ends_prototype = ends_prototype

        apply_braces(code, scope_stack)

    return output
