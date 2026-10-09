#!/usr/bin/env python3
"""
Step-by-step builders turning a raw declaration line into its parts.

Each helper answers one question of the assembly: how the initializer splits,
where the variable name sits (skipping an array suffix), and how the aligned
``rest`` is rebuilt. All indexes come from the masked copy while the returned
slices stay identical to the source text.
"""

import re

from shared.declaration_parse.keywords import RESERVED_NAMES
from shared.declaration_parse.literal_mask import mask_literals
from shared.declaration_parse.separators import is_valid_type_part

ARRAY_SUFFIX_REGEX = re.compile(r"(?:\s*\[[^\[\]]*\])+\s*$")

IDENTIFIER_TAIL_REGEX = re.compile(r"[A-Za-z_]\w*$")

SPACE_BEFORE_SEMICOLON_REGEX = re.compile(r"\s+;$")

ASSIGNMENT = "="
SEMICOLON = ";"

DEPTH_OPEN_CHARS = ("<", "(", "[", "{")
DEPTH_CLOSE_CHARS = (">", ")", "]", "}")
SEPARATOR = ","


def has_top_level_comma(text: str) -> bool:
    """Detect a comma separating several declarators inside an initializer."""
    depth = 0
    for char in text:
        if char in DEPTH_OPEN_CHARS:
            depth += 1
        elif char in DEPTH_CLOSE_CHARS:
            depth = max(0, depth - 1)
        elif char == SEPARATOR and depth == 0:
            return True
    return False


def split_initializer(body: str, split: int, stripped: str) -> tuple[int, str] | None:
    """Return ``(lhs_end, rhs_text)`` or None when several declarators appear."""
    if split < 0:
        return len(body), ""
    rhs_text = SPACE_BEFORE_SEMICOLON_REGEX.sub(SEMICOLON, stripped[split:].strip())
    if has_top_level_comma(mask_literals(stripped[split:])):
        return None
    return split, rhs_text


def locate_variable_name(body: str) -> tuple[int | None, re.Match] | None:
    lhs_masked = body.rstrip()
    array_match = ARRAY_SUFFIX_REGEX.search(lhs_masked)
    array_start = array_match.start() if array_match is not None else None
    if array_start is not None:
        lhs_masked = lhs_masked[:array_start].rstrip()
    name_match = IDENTIFIER_TAIL_REGEX.search(lhs_masked)
    if name_match is None:
        return None
    return array_start, name_match


def resolve_name_and_type(body: str, lhs_end: int, stripped: str) -> tuple[int | None, str, str] | None:
    located = locate_variable_name(body[:lhs_end])
    if located is None:
        return None
    array_start, name_match = located
    name = name_match.group(0)
    if name in RESERVED_NAMES:
        return None
    type_part = stripped[: name_match.start()].rstrip()
    if not is_valid_type_part(type_part):
        return None
    return array_start, name, type_part


def build_rest(stripped: str, array_start: int | None, lhs_end: int, rhs_text: str) -> str:
    array_suffix = stripped[array_start:lhs_end] if array_start is not None else ""
    if rhs_text.startswith(ASSIGNMENT):
        initializer = rhs_text[1:].lstrip()
        if initializer:
            return array_suffix + " = " + initializer
        return array_suffix + SEMICOLON
    if rhs_text:
        return array_suffix + rhs_text
    return array_suffix + SEMICOLON
