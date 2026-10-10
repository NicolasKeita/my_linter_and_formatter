#!/usr/bin/env python3
"""
Function Parameter Count Checks

Warns when a function definition has more than MAX_FUNCTION_PARAMETERS
parameters (five is allowed, six or more is reported). The rule applies
to both .cpp and .cppm files.

The check reuses the sanitizer and block-classification logic from
cppm_inline_function_checks to identify function definitions (an opening
brace at parenthesis depth zero whose preceding header is classified as a
function). For each function the parameter list is extracted and the
top-level commas are counted; commas nested inside parentheses, angle
brackets, square brackets and braces are ignored so that function-pointer
parameters, template arguments and braced default values are handled
correctly.
"""

from linter.module.cppm_inline_function_checks import _sanitize_code

from .scan import _scan_for_parameter_count

MAX_FUNCTION_PARAMETERS = 5

WARN_FUNCTION_TOO_MANY_PARAMETERS_TAG = "[WARN_FUNCTION_TOO_MANY_PARAMETERS]"


def check_function_parameter_count(
    code: str,
    max_params: int = MAX_FUNCTION_PARAMETERS,
) -> list[tuple[str, int, int]]:
    """
    Report functions whose parameter count exceeds max_params.

    Returns a list of (function_name, start_line, parameter_count) tuples.
    Only function definitions (with a body) are checked; declarations and
    function calls are not affected.
    """
    sanitized = _sanitize_code(code)
    return _scan_for_parameter_count(sanitized, max_params)


def format_function_parameter_count_message(
    file_path: str,
    function_name: str,
    start_line: int,
    param_count: int,
) -> str:
    return (
        f"{WARN_FUNCTION_TOO_MANY_PARAMETERS_TAG} {file_path}:{start_line} : "
        f"la fonction '{function_name}' possède {param_count} paramètres "
        f"(max : {MAX_FUNCTION_PARAMETERS}). "
        "Envisagez de regrouper certains paramètres dans une structure ou classe."
    )
