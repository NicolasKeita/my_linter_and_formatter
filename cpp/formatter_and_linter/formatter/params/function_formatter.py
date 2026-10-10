#!/usr/bin/env python3
"""
Function Parameter Formatting

Public entry points for function parameter formatting. The implementation
lives in parameter_parser, parameter_formatter and multiline_function_formatter.

Formats C++ function parameters for readability: handles single-line and
multi-line signatures, parameter alignment and spacing.
"""

import re

from formatter.params.multiline_function_formatter import format_multiline_function_params
from formatter.params.parameter_formatter import (
    PARAM_NAME_SEPARATOR_WIDTH,
    calculate_alignment,
    calculate_indentation,
    format_parameters_list,
    format_single_function,
    should_format_function,
)
from formatter.params.parameter_parser import extract_parameters, parse_parameter


def _single_line_function_pattern() -> str:
    """Build the anchored single-line function-definition pattern.

    Parameters cannot cross ';' or braces, so preprocessor directives
    such as '#if defined(_WIN32)' are never consumed as part of a signature.
    """
    return (
        r"^([ \t]*)"
        r"((?:(?:static|inline|virtual|explicit|constexpr|const)\s+)*[\w:]+(?:\s*[*&])*)"
        r"\s+(\w+)\s*\(([^;{}]*?)\)\s*"
        r"((?:const\b\s*|noexcept\b(?:\s*\([^()]*\))?\s*|override\b\s*|final\b\s*)*)"
        r"\{"
    )


def format_function_params(code: str) -> str:
    """
    Format function parameters in C++ code for better readability.

    Args:
        code: The C++ code as a string

    Returns:
        The formatted code
    """
    pattern = _single_line_function_pattern()
    formatted = re.sub(pattern, format_single_function, code, flags=re.MULTILINE)
    return format_multiline_function_params(formatted)


__all__ = [
    "parse_parameter",
    "extract_parameters",
    "PARAM_NAME_SEPARATOR_WIDTH",
    "calculate_alignment",
    "calculate_indentation",
    "format_parameters_list",
    "should_format_function",
    "format_single_function",
    "format_multiline_function_params",
    "format_function_params",
]
