#!/usr/bin/env python3
"""Multi-line Function Parameter Formatter

Re-formats C++ function definitions whose parameters are already spread over
several lines.
"""

import re

from formatter.params.parameter_formatter import (
    calculate_alignment,
    calculate_indentation,
    format_parameters_list,
)
from formatter.params.parameter_parser import extract_parameters
from formatter.params.multiline_signature_formatter import (
    _SignatureParts,
    _try_format_signature,
)

SIGNATURE_PATTERN = (
    r"^(\s*)((?:(?:static|inline|virtual|explicit|constexpr|const)\s+)*[\w:]+(?:\s*[*&])*)\s+([\w:]+)\s*\("
)


def format_multiline_function_params(code: str) -> str:
    """
    Format multi-line function parameters in C++ code for better readability.
    This handles cases where function parameters are already on multiple lines.

    Args:
        code: The C++ code as a string

    Returns:
        The formatted code
    """
    lines = code.splitlines()
    result_lines = []
    i = 0

    while i < len(lines):
        match = re.match(SIGNATURE_PATTERN, lines[i])
        formatted = _try_format_signature(lines, i, match) if match else None
        if formatted is None:
            result_lines.append(lines[i])
            i += 1
            continue
        emitted, i = formatted
        result_lines.extend(emitted)

    return "\n".join(result_lines)
