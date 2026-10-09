#!/usr/bin/env python3
"""
Public entry point that turns one C++ declaration line into its parts.

``parse_declaration`` chains the lower-level helpers: it masks the line, finds
the declaration split, resolves the variable name and type, then rebuilds the
aligned ``rest``. Anything not safely recognisable as a single variable
declaration yields ``None`` so callers leave it untouched.
"""

from typing import NamedTuple

from shared.declaration_parse.declaration_assembly import (
    build_rest,
    resolve_name_and_type,
    split_initializer,
)
from shared.declaration_parse.literal_mask import mask_literals
from shared.declaration_parse.separators import find_declaration_split


class DeclarationParts(NamedTuple):
    """One parsed variable declaration line ready to be realigned."""

    indent: str
    type_part: str
    name: str
    rest: str
    comment: str
    original_line: str


def _resolve_split(code_part: str, allow_paren_init: bool) -> tuple[str, int, str] | None:
    """Return ``(body, lhs_end, rhs_text)`` or None when unparsable."""
    stripped = code_part.strip()
    if not stripped.endswith(";") or "/*" in stripped:
        return None
    body = mask_literals(stripped)[:-1].rstrip()
    split = find_declaration_split(body, allow_paren_init)
    if split is None:
        return None
    initializer = split_initializer(body, split, stripped)
    if initializer is None:
        return None
    lhs_end, rhs_text = initializer
    return body, lhs_end, rhs_text


def parse_declaration(
    code_part: str,
    comment: str,
    original_line: str,
    allow_paren_init: bool = False,
) -> DeclarationParts | None:
    """Parse one 'Type name = init;' / 'Type name{init};' / 'Type name(args);'
    declaration line.

    Indexes are computed on a length-preserving masked copy of the line
    (literals and inline block comments replaced by spaces) while every
    extracted slice is taken from the original text, so initializers keep
    their exact content. Returns None for anything that is not safely
    recognisable as a single variable declaration.

    ``allow_paren_init`` enables the constructor-call form 'Type name(args);'
    used by function-local declarations; it is False by default to keep the
    member-alignment pass (class bodies) conservative.
    """
    resolved = _resolve_split(code_part, allow_paren_init)
    if resolved is None:
        return None
    body, lhs_end, rhs_text = resolved
    stripped = code_part.strip()
    named = resolve_name_and_type(body, lhs_end, stripped)
    if named is None:
        return None
    array_start, name, type_part = named
    return DeclarationParts(
        indent=code_part[: len(code_part) - len(code_part.lstrip())],
        type_part=type_part,
        name=name,
        rest=build_rest(stripped, array_start, lhs_end, rhs_text),
        comment=comment.strip(),
        original_line=original_line,
    )
