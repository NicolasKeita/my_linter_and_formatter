#!/usr/bin/env python3
"""
C++ Code Linter — public facade.

Provides :func:`lint_code` (per-file diagnostics) and re-exports the
directory / module / CMake structure checks consumed by the package entry
point. Individual style and language checks live in their own submodules
(``linter.core.*`` and ``linter.module.*``).
"""

import sys

from linter.core.linter._checks import (
    _collect_source_checks,
    collect_cppm_checks,
    print_cppm_warnings,
    print_source_warnings,
)
from linter.core.directory_checks import (
    MAX_FILES_PER_DIRECTORY,
    check_directory_file_counts,
)
from linter.core.reporting import (
    print_cmake_length_warnings,
    print_directory_file_count_warnings,
    print_issue_header,
    print_module_filename_warnings,
    print_module_size_warnings,
)
from linter.module.cmake_checks import (
    MAX_CMAKELISTS_LINES,
    check_cmake_file_lengths,
)
from linter.module.module_filename_checks import check_module_filename_convention
from linter.module.module_size_checks import check_module_implementation_counts



def _lint_cppm(code: str, file_path: str) -> bool:
    results = collect_cppm_checks(code, file_path)
    has_issues = (
        len(results["cppm_violations"]) > 0
        or results["file_too_long"]
        or len(results["language_violations"]) > 0
        or len(results["multiple_decl_violations"]) > 0
        or len(results["uninitialized_decl_violations"]) > 0
        or len(results["designated_init_violations"]) > 0
        or len(results["return_only_var_violations"]) > 0
        or len(results["main_filename_violations"]) > 0
        or len(results["param_count_violations"]) > 0
    )
    if has_issues:
        print_issue_header(file_path)
    print_cppm_warnings(results, file_path)
    return has_issues


def _has_source_issues(results: dict) -> bool:
    return (
        len(results["long_lines"]) > 0
        or len(results["invalid_comments"]) > 0
        or len(results["long_functions"]) > 0
        or len(results["blank_line_violations"]) > 0
        or results["file_too_long"]
        or len(results["language_violations"]) > 0
        or len(results["multiple_decl_violations"]) > 0
        or len(results["uninitialized_decl_violations"]) > 0
        or len(results["designated_init_violations"]) > 0
        or len(results["return_only_var_violations"]) > 0
        or len(results["main_filename_violations"]) > 0
        or len(results["param_count_violations"]) > 0
    )


def lint_code(code: str, max_length: int = 120, file_path: str = "") -> bool:
    is_module_interface = file_path.lower().endswith('.cppm')
    if is_module_interface:
        return _lint_cppm(code, file_path)

    results = _collect_source_checks(code, max_length, file_path)
    has_issues = _has_source_issues(results)
    if has_issues:
        print_issue_header(file_path)
        print_source_warnings(results, max_length)

    return has_issues


__all__ = [
    "lint_code",
    "check_directory_file_counts",
    "MAX_FILES_PER_DIRECTORY",
    "print_directory_file_count_warnings",
    "check_module_filename_convention",
    "print_module_filename_warnings",
    "check_module_implementation_counts",
    "print_module_size_warnings",
    "check_cmake_file_lengths",
    "MAX_CMAKELISTS_LINES",
    "print_cmake_length_warnings",
    "print_issue_header",
]


if __name__ == "__main__":
    code = sys.stdin.read()
    has_issues = lint_code(code)
    sys.exit(1 if has_issues else 0)

