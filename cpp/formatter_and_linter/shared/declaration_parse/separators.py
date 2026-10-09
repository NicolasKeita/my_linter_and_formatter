#!/usr/bin/env python3
"""
Locating the initializer separator and validating the type part.

`find_declaration_split` walks a declaration body and reports where the type and
the variable name end; `is_valid_type_part` checks that the remaining text can
only be a C++ type (namespaced name, template, qualifiers, pointers...).
"""

import re

from shared.declaration_parse.keywords import NON_TYPE_KEYWORDS

IDENTIFIER_REGEX = re.compile(r"[A-Za-z_]\w*")

INTEGER_LITERAL_REGEX = re.compile(r"-?\d+")

TYPE_TOKEN_REGEX = re.compile(r"[A-Za-z_]\w*|::|[<>*&\[\]]|\S")

NO_SPLIT_CHARS = (",", ";")
STRUCTURAL_TOKENS = ("::", "*", "&", "[", "]")
PAIR_TOKENS = ("(", ")")
NO_INITIALIZER = -1

ANGLE_OPEN = "<"
ANGLE_CLOSE = ">"
PAREN_OPEN = "("
PAREN_CLOSE = ")"
COMMA = ","
ASSIGNMENT_CHARS = ("=", "{")


def _track_angle_depth(angle_depth: int, char: str) -> int:
    if char == ANGLE_OPEN:
        return angle_depth + 1
    if char == ANGLE_CLOSE and angle_depth > 0:
        return angle_depth - 1
    return angle_depth


def find_declaration_split(body: str, allow_paren_init: bool = False) -> int | None:
    """Locate the first top-level '=' or '{' separating 'type name' from its
    initializer.

    Returns the index of the separator, -1 when the declaration carries no
    initializer, or None when the line cannot be a single variable
    declaration (commas / extra semicolons at top level, i.e. methods,
    multiple declarators or function pointers).

    By default a top-level '(' also yields None: inside a class body a '(' is
    ambiguous (it can start a function pointer or a member function). For
    function-local declarations a '(' instead opens a constructor-call
    initializer ('Type name(args);'), which is legal there, so callers can
    pass ``allow_paren_init=True`` to treat it as a split point.
    """
    angle_depth = 0
    for index, char in enumerate(body):
        angle_depth = _track_angle_depth(angle_depth, char)
        if angle_depth != 0:
            continue
        if char == PAREN_OPEN:
            return index if allow_paren_init else None
        if char == PAREN_CLOSE or char in NO_SPLIT_CHARS:
            return None
        if char in ASSIGNMENT_CHARS:
            return index
    return NO_INITIALIZER


def _accepts_structural_token(token: str, angle_depth: int) -> bool:
    if token in STRUCTURAL_TOKENS:
        return True
    if token in PAIR_TOKENS or token == COMMA:
        return angle_depth > 0
    if IDENTIFIER_REGEX.fullmatch(token):
        return True
    return angle_depth > 0 and INTEGER_LITERAL_REGEX.fullmatch(token) is not None


def is_valid_type_part(type_part: str) -> bool:
    """Check that the text before the variable name looks like a C++ type."""
    if not type_part:
        return False
    tokens = TYPE_TOKEN_REGEX.findall(type_part)
    if not tokens or tokens[0] in NON_TYPE_KEYWORDS:
        return False
    angle_depth = 0
    for token in tokens:
        if token == ANGLE_OPEN:
            angle_depth += 1
            continue
        if token == ANGLE_CLOSE:
            if angle_depth == 0:
                return False
            angle_depth -= 1
            continue
        if not _accepts_structural_token(token, angle_depth):
            return False
    return angle_depth == 0
