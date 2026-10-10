#!/usr/bin/env python3
"""Parsing of a local declaration line for the alignment pass."""

from typing import NamedTuple

from shared.declaration_parse import (
    DeclarationParts,
    mask_literals,
    parse_declaration,
    split_trailing_comment,
)


class StatementBlock(NamedTuple):
    """One logical declaration statement of an alignment block.

    ``parts`` carries the indent / type / name parsed from the statement's
    first line, ``tail`` is the raw text that follows the name on that line
    ('{', ' = make(', ' = 1;', ...), ``continuation`` holds the verbatim
    continuation lines of a multi-line statement and ``original_line`` is the
    untouched first line, used when the block is emitted without alignment.
    """

    parts: DeclarationParts
    tail: str
    continuation: tuple[str, ...]
    original_line: str


def _parse_local_declaration(line: str) -> DeclarationParts | None:
    """Parse a single function-body line as a local variable declaration.

    Trailing line comments are split off first (and re-attached by the caller)
    and the constructor-call form 'Type name(args);' is accepted through the
    shared parser's ``allow_paren_init`` flag, which is only meaningful at
    function scope.
    """
    code_part, comment, _ = split_trailing_comment(line, False)
    if not code_part.strip().endswith(";"):
        return None
    return parse_declaration(code_part, comment, line, allow_paren_init=True)


def _parse_statement_start(line: str) -> tuple[DeclarationParts, str] | None:
    """Parse the first line of a multi-line declaration statement.

    The line must end with an opened brace or parenthesis initializer
    ('Type name{', 'Type name(' or 'Type name = make('). The declaration is
    parsed from a probe line where the opened initializer is temporarily
    closed, and the raw text following the variable name on the original line
    is returned alongside the parsed parts so the caller can rebuild the line
    with alignment while keeping the opened initializer verbatim.
    """
    code_part, comment, _ = split_trailing_comment(line, False)
    stripped = code_part.rstrip()
    if not stripped.endswith(("(", "{")):
        return None
    probe = stripped[:-1].rstrip() + ";"
    if probe == ";":
        return None
    parsed = parse_declaration(probe, comment, line, allow_paren_init=True)
    if parsed is None:
        return None
    masked_head = mask_literals(stripped[:-1])
    name_start = masked_head.find(parsed.name, len(parsed.indent) + len(parsed.type_part))
    if name_start < 0:
        return None
    tail = stripped[name_start + len(parsed.name):]
    return parsed, tail
