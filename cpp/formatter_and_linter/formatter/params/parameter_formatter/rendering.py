#!/usr/bin/env python3
"""Aligned rendering of a C++ function parameter list."""

PARAM_NAME_SEPARATOR_WIDTH = 1


def _first_param_line(ptype: str, pname: str, max_type_len: int) -> str:
    """Render the first parameter, which stays on the function-name line."""
    formatted_type = ptype.ljust(max_type_len)
    separator = " " * PARAM_NAME_SEPARATOR_WIDTH
    return f"({formatted_type}{separator}{pname},"


def _middle_param_line(ptype: str, pname: str, indent: str, max_type_len: int) -> str:
    formatted_type = ptype.ljust(max_type_len)
    separator = " " * PARAM_NAME_SEPARATOR_WIDTH
    return f"{indent}{formatted_type}{separator}{pname},"


def _last_param_line(ptype: str, pname: str, indent: str, max_type_len: int) -> str:
    formatted_type = ptype.ljust(max_type_len)
    separator = " " * PARAM_NAME_SEPARATOR_WIDTH
    return f"{indent}{formatted_type}{separator}{pname})"


def format_parameters_list(
    parsed_params: list[tuple[str, str]],
    indent: str,
    max_type_len: int
) -> str:
    """
    Format a list of parameters with proper alignment.

    Args:
        parsed_params: List of (type, name) tuples
        indent: The indentation string
        max_type_len: Maximum type length for alignment

    Returns:
        Formatted parameter list as a string
    """
    lines = []

    for i, (ptype, pname) in enumerate(parsed_params):
        if i == 0:
            line = _first_param_line(ptype, pname, max_type_len)
        elif i < len(parsed_params) - 1:
            line = _middle_param_line(ptype, pname, indent, max_type_len)
        else:
            line = _last_param_line(ptype, pname, indent, max_type_len)

        lines.append(line)

    return '\n'.join(lines)
