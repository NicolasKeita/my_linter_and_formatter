#!/usr/bin/env python3
"""
Per-line brace scanner that skips strings and comments.

``find_brace_positions`` returns the ``(index, character)`` of every ``{`` or
``}`` that is neither inside a string / char literal nor inside a ``//`` or
``/* */`` comment.
"""

QUOTE_CHARS = ('"', "'")
BLOCK_COMMENT = "block"
LINE_COMMENT = "line"
STRING = "string"
CODE = "code"
BLOCK_COMMENT_END = "*/"
ESCAPE = "\\"


def _opens_comment(i: int, line: str) -> tuple[str, int] | None:
    char = line[i]
    following = line[i + 1] if i + 1 < len(line) else ""
    if char == "/" and following == "/":
        return LINE_COMMENT, i + 2
    if char == "/" and following == "*":
        return BLOCK_COMMENT, i + 2
    return None


def _code_transition(i: int, line: str, positions: list[tuple[int, str]]) -> tuple[str, int, str] | None:
    opened = _opens_comment(i, line)
    if opened is not None:
        state, next_index = opened
        return state, next_index, ""
    if line[i] in QUOTE_CHARS:
        return STRING, i + 1, line[i]
    if line[i] in ("{", "}"):
        positions.append((i, line[i]))
    return None


def find_brace_positions(line: str) -> list[tuple[int, str]]:
    positions: list[tuple[int, str]] = []
    state = CODE
    string_char = ""
    i = 0
    while i < len(line):
        char = line[i]
        following = line[i + 1] if i + 1 < len(line) else ""
        if state == CODE:
            transition = _code_transition(i, line, positions)
            if transition is None:
                if char == ESCAPE:
                    i += 1
                i += 1
                continue
            state, i, string_char = transition
            continue
        if state == LINE_COMMENT:
            break
        if state == BLOCK_COMMENT:
            if char == "*" and following == "/":
                state = CODE
                i += 2
                continue
            i += 1
            continue
        if char == ESCAPE:
            i += 2
            continue
        if char == string_char:
            state = CODE
        i += 1
    return positions
