#!/usr/bin/env python3
"""Parameter formatting package for C++ function declarations/definitions."""

from formatter.params.parameter_formatter.alignment import (
    calculate_alignment,
    calculate_indentation,
)
from formatter.params.parameter_formatter.rendering import (
    PARAM_NAME_SEPARATOR_WIDTH,
    format_parameters_list,
)

from formatter.params.parameter_parser import extract_parameters


__all__ = [
    "PARAM_NAME_SEPARATOR_WIDTH",
    "calculate_alignment",
    "calculate_indentation",
    "format_parameters_list",
    "should_format_function",
    "format_single_function",
]


def should_format_function(prefix: str, func_name: str, params_str: str) -> bool:
    """
    Determine if a function should be formatted.

    Args:
        prefix: The function prefix
        func_name: The function name
        params_str: The parameter string

    Returns:
        True if the function should be formatted, False otherwise
    """
    if not params_str.strip():
        return False

    if '\n' not in params_str:
        return False

    return True


def format_single_function(match: Match[str]) -> str:
    """
    Format a single function's parameters.

    Args:
        match: Regex match object containing function components

    Returns:
        Formatted function string
    """
    leading_indent = match.group(1)
    full_prefix = match.group(2)
    func_name = match.group(3)
    params_str = match.group(4)
    signature_suffix = match.group(5).strip()

    if not should_format_function(full_prefix, func_name, params_str):
        return match.group(0)

    parsed_params = extract_parameters(params_str)

    if not parsed_params:
        return match.group(0)

    max_type_len, max_name_len = calculate_alignment(parsed_params)

    indent = calculate_indentation(full_prefix, func_name, max_type_len)

    formatted_params = format_parameters_list(parsed_params, indent, max_type_len)

    const_part = f" {signature_suffix}" if signature_suffix else ""
    return f"{leading_indent}{full_prefix} {func_name}{formatted_params}{const_part}\n{{\""