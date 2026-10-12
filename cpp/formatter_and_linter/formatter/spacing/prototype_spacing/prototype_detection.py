#!/usr/bin/env python3
"""Heuristics to recognise function prototypes for blank-line collapsing."""

from formatter.spacing.prototype_spacing.patterns import (
    CONTROL_STATEMENT_REGEX,
    DELETE_DEFAULT_REGEX,
    FUNCTION_CALL_REGEX,
    NAMESPACE_OPEN_REGEX,
    NON_PROTOTYPE_REGEX,
)


def paren_balance(code: str) -> int:
    return code.count("(") - code.count(")")


def is_prototype_candidate(code: str) -> bool:
    stripped = code.strip()

    if not stripped or stripped.startswith("#"):
        return False
    if "{" in stripped or "}" in stripped:
        return False
    if "(" not in stripped:
        return False
    if NON_PROTOTYPE_REGEX.match(stripped):
        return False
    if CONTROL_STATEMENT_REGEX.match(stripped):
        return False
    if DELETE_DEFAULT_REGEX.search(stripped):
        return False
    if not FUNCTION_CALL_REGEX.search(stripped):
        return False

    return True


def looks_like_prototype(code: str) -> bool:
    stripped = code.strip()

    if not stripped.endswith(";"):
        return False
    if ")" not in stripped:
        return False

    return is_prototype_candidate(code)


def looks_like_prototype_start(code: str) -> bool:
    stripped = code.strip()

    if stripped.endswith(";"):
        return False

    return is_prototype_candidate(code)


def apply_braces(code: str, scope_stack: list[str]) -> None:
    prefix_chars = []

    for char in code:
        if char == "{":
            prefix = "".join(prefix_chars).strip()
            if NAMESPACE_OPEN_REGEX.search(prefix):
                scope_stack.append("namespace")
            else:
                scope_stack.append("other")
            prefix_chars = []
        elif char == "}":
            prefix_chars = []
            if scope_stack:
                scope_stack.pop()
        else:
            prefix_chars.append(char)


def multiline_signature_ends_as_prototype(stripped: list[str], start: int) -> bool:
    balance = 0

    for index in range(start, len(stripped)):
        code = stripped[index]

        if index > start and code.strip() == "":
            continue

        balance += paren_balance(code)

        if "{" in code:
            return False

        if balance <= 0:
            return code.strip().endswith(";")

    return False
