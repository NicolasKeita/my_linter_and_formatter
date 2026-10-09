#!/usr/bin/env python3
"""
Utilities for function context analysis in C++ code.

Provides functions for detecting function definition context, finding function
starts, and checking multiline function signatures.
"""

from shared.function_analysis.definition_context import (
    check_multiline_function_signature,
    is_function_definition_context,
)
from shared.function_analysis.qualifiers import strip_trailing_qualifiers
from shared.function_analysis.start_finder import find_function_start_for_brace
from shared.function_analysis.stream_operators import has_stream_operators

__all__ = [
    "has_stream_operators",
    "is_function_definition_context",
    "check_multiline_function_signature",
    "strip_trailing_qualifiers",
    "find_function_start_for_brace",
]
