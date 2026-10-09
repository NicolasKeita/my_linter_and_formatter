#!/usr/bin/env python3
"""
Utilities for brace detection and analysis in C++ code.

Provides state-machine helpers for identifying braces in function definitions,
lambdas, initializer lists, and control structures. The low-level per-line
scanner lives in :mod:`shared.brace_utils.brace_scanner`.
"""

import re

from shared.brace_utils.brace_scanner import find_brace_positions
from shared.brace_utils.keywords import CONTROL_KEYWORDS
from shared.brace_utils.signature import extract_function_name


def is_control_structure(line: str) -> bool:
    stripped = line.strip()
    for keyword in ['if', 'while', 'for', 'switch', 'catch']:
        pattern = rf'^{keyword}\s*\('
        if re.match(pattern, stripped):
            return True
    return False


def is_lambda_capture(line: str, brace_pos: int) -> bool:
    before_brace = line[:brace_pos]
    bracket_pattern = r'\[[^\]]*\]\s*$'
    return bool(re.search(bracket_pattern, before_brace))


def is_initializer_list(line: str, brace_pos: int) -> bool:
    before_brace = line[:brace_pos].rstrip()
    if before_brace.endswith('='):
        return True
    type_brace_pattern = r'\w+\s*\{[^}]*\}'
    if re.search(type_brace_pattern, line):
        return True
    return False


def is_constructor_initializer_continuation(line_prefix: str) -> bool:
    stripped = line_prefix.strip()
    return stripped.startswith(':') or stripped.startswith(',')


def brace_delta(line: str) -> int:
    """Net change in brace depth introduced by ``line`` (opens minus closes),
    ignoring braces inside string / char literals and comments."""
    positions = find_brace_positions(line)
    opens = sum(1 for _, char in positions if char == '{')
    closes = sum(1 for _, char in positions if char == '}')
    return opens - closes


__all__ = [
    "CONTROL_KEYWORDS",
    "brace_delta",
    "extract_function_name",
    "find_brace_positions",
    "is_constructor_initializer_continuation",
    "is_control_structure",
    "is_initializer_list",
    "is_lambda_capture",
]
