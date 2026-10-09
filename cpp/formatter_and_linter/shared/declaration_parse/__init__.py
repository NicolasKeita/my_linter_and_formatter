#!/usr/bin/env python3
"""
Declaration type / name parsing primitives shared by the alignment passes.

Centralises the low-level parsing used to split a single C++ variable
declaration line ('Type name = init;', 'Type name{init};', 'Type name(args);',
'Type name;') into its indentation, the full type part that precedes the
variable name, the variable name and the trailing initializer. Everything is
computed on a length-preserving masked copy of the line so string / char
literals and inline block comments never disturb the brace / separator scans
while the extracted slices stay byte-identical to the source.

Complex types are supported: namespaced names ('a::b::C'), templates
('<...>', nested and containing commas or integer literals), fixed-width types
('std::uint64_t'), qualifiers ('const', 'static', 'constexpr', 'mutable',
'unsigned', ...), pointers and references, array suffixes ('[3]', '[N][M]')
and leading attributes. Declarations that cannot be parsed with certainty
(bit-fields, function pointers, multiple declarators, elaborated type
specifiers, reserved-word names, ...) yield None so callers leave them
untouched.
"""

import re

from shared.declaration_parse.comment_split import split_trailing_comment
from shared.declaration_parse.declaration_assembly import has_top_level_comma
from shared.declaration_parse.keywords import NON_TYPE_KEYWORDS, RESERVED_NAMES
from shared.declaration_parse.literal_mask import mask_literals
from shared.declaration_parse.parse import DeclarationParts, parse_declaration
from shared.declaration_parse.separators import (
    IDENTIFIER_REGEX,
    find_declaration_split,
    is_valid_type_part,
)

ARRAY_SUFFIX_REGEX = re.compile(r"(?:\s*\[[^\[\]]*\])+\s*$")

IDENTIFIER_TAIL_REGEX = re.compile(r"[A-Za-z_]\w*$")

SPACE_BEFORE_SEMICOLON_REGEX = re.compile(r"\s+;$")

__all__ = [
    "DeclarationParts",
    "mask_literals",
    "split_trailing_comment",
    "find_declaration_split",
    "is_valid_type_part",
    "has_top_level_comma",
    "parse_declaration",
    "IDENTIFIER_REGEX",
    "IDENTIFIER_TAIL_REGEX",
    "ARRAY_SUFFIX_REGEX",
    "TYPE_TOKEN_REGEX",
    "INTEGER_LITERAL_REGEX",
    "SPACE_BEFORE_SEMICOLON_REGEX",
    "NON_TYPE_KEYWORDS",
    "RESERVED_NAMES",
]
