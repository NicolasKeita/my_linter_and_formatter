#!/usr/bin/env python3
"""Alignment and indentation computation for C++ function parameters."""


def calculate_alignment(parsed_params: list[tuple[str, str]]) -> tuple[int, int]:
    """
    Calculate the maximum lengths for type and name alignment.

    Args:
        parsed_params: List of (type, name) tuples

    Returns:
        A tuple of (max_type_length, max_name_length)
    """
    if not parsed_params:
        return 0, 0

    max_type_len = max(len(ptype) for ptype, _ in parsed_params)
    max_name_len = max(len(pname) for _, pname in parsed_params)

    return max_type_len, max_name_len


def calculate_indentation(prefix: str, func_name: str, max_type_len: int, leading_indent: str = "") -> str:
    """
    Calculate the indentation for parameter formatting.

    Args:
        prefix: The function prefix (modifiers, return type)
        func_name: The function name
        max_type_len: Maximum type length for alignment

    Returns:
        The indentation string
    """
    first_param_type_start = len(leading_indent) + len(prefix) + 1 + len(func_name) + 1
    return ' ' * first_param_type_start
