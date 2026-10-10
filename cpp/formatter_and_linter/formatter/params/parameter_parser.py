#!/usr/bin/env python3
"""
Parameter Parser

Parsing utilities for C++ function parameters: splits a parameter string into
individual (type, name) tuples.
"""

import re

MAYBE_UNUSED_PATTERN = r"^(.*?\[\[maybe_unused\]\].*?)\s+(\w+)$"
PLAIN_PARAM_PATTERN = r"^(.+?)\s+(\w+)$"


def _split_type_and_name(param: str, pattern: str) -> tuple[str, str] | None:
    type_match = re.match(pattern, param)
    if type_match:
        return (type_match.group(1).strip(), type_match.group(2).strip())
    return None


def parse_parameter(param: str) -> tuple[str, str] | None:
    """
    Parse a single parameter string into type and name.

    Args:
        param: The parameter string to parse

    Returns:
        A tuple of (type, name) if parsing succeeds, None otherwise
    """
    param = param.strip()

    if "[[maybe_unused]]" in param:
        found = _split_type_and_name(param, MAYBE_UNUSED_PATTERN)
        if found is not None:
            return found

    return _split_type_and_name(param, PLAIN_PARAM_PATTERN)


def extract_parameters(params_str: str) -> list[tuple[str, str]] | None:
    """
    Extract and parse all parameters from a parameter string.

    Args:
        params_str: The parameter string from a function signature

    Returns:
        A list of (type, name) tuples if all parameters parse successfully,
        None if any parameter fails to parse
    """
    params = []
    current_param = ""
    bracket_depth = 0
    square_depth = 0

    for char in params_str:
        if char == '<':
            bracket_depth += 1
            current_param += char
        elif char == '>':
            bracket_depth -= 1
            current_param += char
        elif char == '[':
            square_depth += 1
            current_param += char
        elif char == ']':
            square_depth -= 1
            current_param += char
        elif char == ',' and bracket_depth == 0 and square_depth == 0:
            if current_param.strip():
                params.append(current_param.strip())
            current_param = ""
        else:
            current_param += char

    if current_param.strip():
        params.append(current_param.strip())

    parsed_params = []
    for param in params:
        parsed = parse_parameter(param)
        if parsed:
            parsed_params.append(parsed)
        else:
            return None

    return parsed_params
