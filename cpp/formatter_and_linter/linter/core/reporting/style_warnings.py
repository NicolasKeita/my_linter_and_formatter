#!/usr/bin/env python3
"""Reporting for style-level warnings (declarations, init, params)."""

import sys

from linter.core.reporting._path_label import get_path_label
from linter.style.designated_init_checks import format_designated_init_message
from linter.style.function_parameter_count_checks import (
    format_function_parameter_count_message,
)
from linter.style.multiple_var_decl_checks import MULTIPLE_VAR_DECL_MESSAGE
from linter.style.return_only_var_checks import format_return_only_var_message
from linter.style.uninitialized_decl_checks import format_uninitialized_decl_message


def print_blank_line_after_initialization_warnings(
    violations: list[tuple[str, int, int]],
) -> None:
    for func_name, func_start, last_decl_line in violations:
        print(
            f"⚠️  Function '{func_name}' at line {func_start}: missing blank line "
            f"after first declaration block (last declaration at line {last_decl_line})",
            file=sys.stderr,
        )


def print_multiple_var_decl_warnings(violations: list[int]) -> None:
    for line_num in violations:
        print(f"⚠️  Line {line_num}: {MULTIPLE_VAR_DECL_MESSAGE}", file=sys.stderr)


def print_uninitialized_decl_warnings(violations: list[tuple[int, str]]) -> None:
    for line_num, variable_name in violations:
        message = format_uninitialized_decl_message(variable_name)
        print(f"⚠️  Line {line_num}: {message}", file=sys.stderr)


def print_designated_init_warnings(
    violations: list[tuple[int, str, str, list[str]]],
) -> None:
    for line_num, type_name, variable_name, field_chains in violations:
        message = format_designated_init_message(type_name, variable_name, field_chains)
        print(f"⚠️  Line {line_num}: {message}", file=sys.stderr)


def print_return_only_var_warnings(violations: list[tuple[int, str]]) -> None:
    for line_num, variable_name in violations:
        message = format_return_only_var_message(variable_name)
        print(f"⚠️  Line {line_num}: {message}", file=sys.stderr)


def print_function_parameter_count_warnings(
    violations: list[tuple[str, int, int]],
    file_path: str,
) -> None:
    path_label = get_path_label(file_path)
    for function_name, start_line, param_count in violations:
        message = format_function_parameter_count_message(
            path_label, function_name, start_line, param_count,
        )
        print(f"⚠️  {message}", file=sys.stderr)
