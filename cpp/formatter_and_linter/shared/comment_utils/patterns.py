#!/usr/bin/env python3
"""
Regex fragments describing C++ function signatures and declarations.

Every fragment is a small building block; :func:`build_function_patterns` and
:func:`build_declaration_patterns` compose them into the full patterns used by
the line classifier.
"""

import re

SCOPED_NAME = r"(?:\w+::)*\w+"

TEMPLATE_TYPE = r"[\w:]+(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?"

FUNCTION_SUFFIX = (
    r"\s*"
    r"(?:(?:const|final|override)\s*|noexcept\s*(?:\([^)]*\)\s*)?)*"
    r"(?:->\s*[\w:<>,&*\s]+?\s*)?"
    r"(?:\s*:\s*[^{;}]+?)?"
    r"\s*(?:\{|$)"
)

ATTRIBUTE_SPECIFIER = r"(?:[ \t]*\[\[[^\]]*\]\])*[ \t]*"

QUALIFIER_PREFIX = r"^[ \t]*(?:static\s+|inline\s+|virtual\s+|explicit\s+|constexpr\s+|const\s+)*"

STORAGE_CLASS_PREFIX = (
    r"^[ \t]*(?:static[ \t]+|inline[ \t]+|constexpr[ \t]+|const[ \t]+|extern[ \t]+|mutable[ \t]+)*"
)

_OPTIONAL_POINTER_TYPE = r"(?:" + TEMPLATE_TYPE + r"[ \t]*[*&]?[ \t]+)+"

_POINTER_TYPE = r"(?:" + TEMPLATE_TYPE + r"\s*[*&]\s+)+"


def _function_signature_variants() -> tuple[str, ...]:
    plain_signature = SCOPED_NAME + r"\s*\([^)]*\)" + FUNCTION_SUFFIX
    return (
        TEMPLATE_TYPE + r"\s+" + plain_signature,
        _POINTER_TYPE + plain_signature,
        _OPTIONAL_POINTER_TYPE + plain_signature,
        r"\w+\s*::\s*\w+\s*\([^)]*\)" + FUNCTION_SUFFIX,
        r"\w+\s*::\s*operator\s*=\s*\([^)]*\)" + FUNCTION_SUFFIX,
    )


def build_function_patterns() -> list[str]:
    """Return the regex strings matching a C++ function signature."""
    head = QUALIFIER_PREFIX + ATTRIBUTE_SPECIFIER
    return [head + variant for variant in _function_signature_variants()]


def build_declaration_patterns() -> list[re.Pattern[str]]:
    """Return the compiled regexes matching a plain C++ declaration line."""
    variable_prefix = STORAGE_CLASS_PREFIX + ATTRIBUTE_SPECIFIER + _OPTIONAL_POINTER_TYPE
    variable_prefix += r"\w+[ \t]*(?:\[[^\]]*\])?[ \t]*(?:=|\{|\(|;)"
    return [
        re.compile(variable_prefix, re.MULTILINE),
        re.compile(r"^[ \t]*(?:struct|class|enum|union)[ \t]+\w+", re.MULTILINE),
        re.compile(
            r"^[ \t]*using[ \t]+[\w:]+(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?[ \t]*=",
            re.MULTILINE,
        ),
    ]


EXCLUDED_DECLARATION_PATTERN = re.compile(r"^[ \t]*(?:import[ \t]|export[ \t]|module[ \t])")

TEMPLATE_PREFIX_PATTERN = re.compile(r"^[ \t]*template\s*<", re.MULTILINE)
