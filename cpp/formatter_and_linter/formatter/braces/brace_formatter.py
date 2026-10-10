#!/usr/bin/env python3
"""
Brace Formatter

Public entry points for brace formatting. The implementation lives in
control_structure_braces, function_braces and advanced_function_braces.

Ensures opening curly braces of function definitions are placed on a new line,
while opening braces of control structures (if, else, for, while, switch,
catch, do, try) are placed on the same line as their header.
"""

from formatter.braces.advanced_function_braces import format_function_braces_advanced
from formatter.braces.control_structure_braces import format_control_structure_braces
from formatter.braces.function_braces import format_function_braces

__all__ = [
    "format_control_structure_braces",
    "format_function_braces",
    "format_function_braces_advanced",
]
