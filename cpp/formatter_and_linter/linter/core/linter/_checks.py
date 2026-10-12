#!/usr/bin/env python3
"""Check-collection and warning-printing helpers used by the linter entry point."""

from linter.core.comment_language_checks import check_code_comments_language
from linter.core.reporting import (
    print_blank_line_after_initialization_warnings,
    print_comment_language_warnings,
    print_comment_placement_warnings,
    print_cppm_inline_function_warnings,
    print_designated_init_warnings,
    print_file_length_warning,
    print_function_length_warnings,
    print_function_parameter_count_warnings,
    print_line_length_warnings,
    print_main_filename_warnings,
    print_multiple_var_decl_warnings,
    print_return_only_var_warnings,
    print_uninitialized_decl_warnings,
)
from linter.module.cppm_inline_function_checks import check_cppm_inline_function_bodies
from linter.module.main_filename_checks import check_main_function_filename
from linter.style.designated_init_checks import check_designated_init_candidates
from linter.style.function_parameter_count_checks import check_function_parameter_count
from linter.style.multiple_var_decl_checks import check_multiple_var_declarations
from linter.style.return_only_var_checks import check_return_only_variable
from linter.style.style_checks import (
    MAX_FILE_LENGTH,
    MAX_FUNCTION_LENGTH,
    check_blank_line_after_initialization,
    check_file_length,
    check_function_length,
    check_line_length,
)
from linter.style.uninitialized_decl_checks import check_uninitialized_declarations
from shared.comment_utils import check_comment_placement, detect_comments_and_functions


def collect_cppm_checks(code: str, file_path: str) -> dict:
    file_too_long, file_line_count = check_file_length(code, max_lines=MAX_FILE_LENGTH)
    return {
        "cppm_violations": check_cppm_inline_function_bodies(code),
        "file_too_long": file_too_long,
        "file_line_count": file_line_count,
        "language_violations": check_code_comments_language(code),
        "multiple_decl_violations": check_multiple_var_declarations(code),
        "uninitialized_decl_violations": check_uninitialized_declarations(code),
        "designated_init_violations": check_designated_init_candidates(code),
        "return_only_var_violations": check_return_only_variable(code),
        "main_filename_violations": check_main_function_filename(code, file_path),
        "param_count_violations": check_function_parameter_count(code),
    }


def _collect_source_checks(code: str, max_length: int, file_path: str) -> dict:
    comments, function_lines, declaration_lines = detect_comments_and_functions(code)
    file_too_long, file_line_count = check_file_length(code, max_lines=MAX_FILE_LENGTH)
    return {
        "long_lines": check_line_length(code, max_length),
        "invalid_comments": check_comment_placement(comments, function_lines, declaration_lines),
        "long_functions": check_function_length(code, max_lines=MAX_FUNCTION_LENGTH),
        "blank_line_violations": check_blank_line_after_initialization(code),
        "file_too_long": file_too_long,
        "file_line_count": file_line_count,
        "language_violations": check_code_comments_language(code),
        "multiple_decl_violations": check_multiple_var_declarations(code),
        "uninitialized_decl_violations": check_uninitialized_declarations(code),
        "designated_init_violations": check_designated_init_candidates(code),
        "return_only_var_violations": check_return_only_variable(code),
        "main_filename_violations": check_main_function_filename(code, file_path),
        "param_count_violations": check_function_parameter_count(code),
    }


def print_cppm_warnings(results: dict, file_path: str) -> None:
    print_cppm_inline_function_warnings(results["cppm_violations"], file_path)
    print_file_length_warning(results["file_too_long"], results["file_line_count"], max_lines=MAX_FILE_LENGTH)
    print_comment_language_warnings(results["language_violations"])
    print_multiple_var_decl_warnings(results["multiple_decl_violations"])
    print_main_filename_warnings(results["main_filename_violations"])
    print_uninitialized_decl_warnings(results["uninitialized_decl_violations"])
    print_designated_init_warnings(results["designated_init_violations"])
    print_return_only_var_warnings(results["return_only_var_violations"])
    print_function_parameter_count_warnings(results["param_count_violations"], file_path)


def print_source_warnings(results: dict, max_length: int) -> None:
    print_line_length_warnings(results["long_lines"], max_length)
    print_comment_placement_warnings(results["invalid_comments"])
    print_function_length_warnings(results["long_functions"], max_lines=MAX_FUNCTION_LENGTH)
    print_blank_line_after_initialization_warnings(results["blank_line_violations"])
    print_file_length_warning(results["file_too_long"], results["file_line_count"], max_lines=MAX_FILE_LENGTH)
    print_comment_language_warnings(results["language_violations"])
    print_multiple_var_decl_warnings(results["multiple_decl_violations"])
    print_main_filename_warnings(results["main_filename_violations"])
    print_uninitialized_decl_warnings(results["uninitialized_decl_violations"])
    print_designated_init_warnings(results["designated_init_violations"])
    print_return_only_var_warnings(results["return_only_var_violations"])
    print_function_parameter_count_warnings(results["param_count_violations"], "")


__all__ = ["collect_cppm_checks", "_collect_source_checks", "print_cppm_warnings", "print_source_warnings"]
