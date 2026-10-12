#!/usr/bin/env python3
"""Shared regex patterns and constants for .cppm interface checks."""

import re

MAX_CPPM_INLINE_BODY_LINES = 1

CPPM_FUNCTION_SIGNATURE_PATTERN = re.compile(
    r'^\s*(?:export\s+)?(?:constexpr\s+|consteval\s+|constinit\s+|inline\s+|static\s+|'
    r'virtual\s+|explicit\s+|friend\s+|extern\s+)*'
    r'[\w:<>,~*&\s]+\s+([\w:~]+)\s*\([^;{}]*\)\s*'
    r'(?:const\s*)?(?:noexcept(?:\s*\([^)]*\))?\s*)?(?:->\s*[\w:<>,~*&\s]+)?\s*\{'
)

CLASS_DECLARATION_REGEX = re.compile(r'^\s*(?:export\s+)?class\s+\w+')

CONTROL_KEYWORDS = {"if", "for", "while", "switch", "catch"}
