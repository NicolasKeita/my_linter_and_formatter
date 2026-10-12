#!/usr/bin/env python3
"""Linter reporting package: warning rendering for the C++ code linter.

Re-exports the print_* helpers from the thematic submodules so existing
callers can keep importing them from ``linter.core.reporting``.
"""

from linter.core.reporting.basic_warnings import (
    print_comment_placement_warnings,
    print_file_length_warning,
    print_function_length_warnings,
    print_issue_header,
    print_line_length_warnings,
)
from linter.core.reporting.directory_module_warnings import (
    print_cmake_length_warnings,
    print_comment_language_warnings,
    print_cppm_inline_function_warnings,
    print_cppm_interface_warnings,
    print_directory_file_count_warnings,
    print_main_filename_warnings,
    print_module_filename_warnings,
    print_module_size_warnings,
)
from linter.core.reporting.style_warnings import (
    print_blank_line_after_initialization_warnings,
    print_designated_init_warnings,
    print_function_parameter_count_warnings,
    print_multiple_var_decl_warnings,
    print_return_only_var_warnings,
    print_uninitialized_decl_warnings,
)

__all__ = [
    "print_issue_header",
    "print_line_length_warnings",
    "print_comment_placement_warnings",
    "print_file_length_warning",
    "print_function_length_warnings",
    "print_comment_language_warnings",
    "print_directory_file_count_warnings",
    "print_module_filename_warnings",
    "print_module_size_warnings",
    "print_cmake_length_warnings",
    "print_main_filename_warnings",
    "print_cppm_interface_warnings",
    "print_cppm_inline_function_warnings",
    "print_blank_line_after_initialization_warnings",
    "print_multiple_var_decl_warnings",
    "print_uninitialized_decl_warnings",
    "print_designated_init_warnings",
    "print_return_only_var_warnings",
    "print_function_parameter_count_warnings",
]
