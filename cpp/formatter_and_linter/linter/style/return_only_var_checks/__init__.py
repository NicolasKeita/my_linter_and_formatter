#!/usr/bin/env python3
"""
Return-Only Variable Checks

Detects local variables that are declared/initialized and then immediately
returned via 'return var;' as their first following executable statement,
ignoring blank lines and comments in between. Any interleaved executable
instruction, a return of a modified expression (member access, call, ...),
or a return of a different identifier cancels the detection.

The declaration may span several lines (braced initializer, designated
initializers, parenthesized constructor call or copy initialization). The
reported line number is the one where the declaration starts.
"""

from .patterns import RETURN_ONLY_VAR_MESSAGE
from .scan import check_return_only_variable


def format_return_only_var_message(variable_name: str) -> str:
    """
    Render the warning message for a variable declared only to be returned
    immediately.
    """
    return RETURN_ONLY_VAR_MESSAGE.format(name=variable_name)


__all__ = ["check_return_only_variable", "format_return_only_var_message"]
