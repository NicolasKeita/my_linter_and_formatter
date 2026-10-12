#!/usr/bin/env python3
"""Regex patterns used by the prototype spacing cleaner."""

import re

NON_BREAKING_SPACE_CHARS = ("\xa0", "\u202f", "\u2007")

NAMESPACE_OPEN_REGEX = re.compile(r"(?:inline\s+|export\s+)*namespace(?:\s+[\w:<>]+)?\s*$")

NON_PROTOTYPE_REGEX = re.compile(r"^\s*(using|typedef|import|module|#|return|case|goto|else|do)\b")

CONTROL_STATEMENT_REGEX = re.compile(r"^\s*(static_assert|noexcept|throw)\s*\(")

DELETE_DEFAULT_REGEX = re.compile(r"\)\s*=\s*(delete|default)\s*;")

FUNCTION_CALL_REGEX = re.compile(r"\w\s*\(")
