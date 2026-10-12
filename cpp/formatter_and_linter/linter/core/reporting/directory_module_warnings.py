#!/usr/bin/env python3
"""Reporting for directory and module-level (cppm/size/filename/cmake) warnings."""

import sys

from linter.core.reporting._path_label import get_path_label
from linter.module.cmake_checks import MAX_CMAKELISTS_LINES
from linter.module.cppm_inline_function_checks import format_cppm_inline_function_message
from linter.module.main_filename_checks import MAIN_FILENAME_MESSAGE
from linter.module.module_size_checks import format_module_too_large_message


def print_comment_language_warnings(violations: list[tuple[int, str]]) -> None:
    for line_num, detected_language in violations:
        print(
            f"⚠️  Line {line_num}: Comment must be written in English "
            f"(detected: {detected_language})",
            file=sys.stderr,
        )


def print_directory_file_count_warnings(
    violations: list[tuple[str, int]],
    max_files: int,
) -> None:
    for directory, file_count in violations:
        print(
            f"⚠️  Directory '{directory}' contains {file_count} source files (max: {max_files}). "
            "Split it into subdirectories.",
            file=sys.stderr,
        )


def print_module_filename_warnings(violations: list[tuple[str, str]]) -> None:
    for file_path, message in violations:
        print(f"⚠️  '{file_path}': {message}", file=sys.stderr)


def print_module_size_warnings(violations: list[tuple[str, int, str]]) -> None:
    for label, file_count, suggestion in violations:
        print(
            f"⚠️  {format_module_too_large_message(label, file_count, suggestion)}",
            file=sys.stderr,
        )


def print_cmake_length_warnings(
    violations: list[tuple[str, int]],
    max_lines: int = MAX_CMAKELISTS_LINES,
) -> None:
    for file_path, line_count in violations:
        print(
            f"⚠️  '{file_path}' exceeds {max_lines} lines: {line_count} lines. "
            "Split the CMake configuration into smaller CMakeLists.txt files.",
            file=sys.stderr,
        )


def print_main_filename_warnings(violations: list[int]) -> None:
    for line_num in violations:
        print(f"⚠️  Line {line_num}: {MAIN_FILENAME_MESSAGE}", file=sys.stderr)


def print_cppm_interface_warnings(
    violations: list[tuple[str, int, int]],
    file_path: str,
) -> None:
    path_label = get_path_label(file_path)
    for function_name, start_line, body_line_count in violations:
        print(
            f"??  {path_label}:{start_line}: Non-trivial implementation in .cppm for "
            f"'{function_name}' ({body_line_count} body lines). Move it to a .cpp file.",
            file=sys.stderr,
        )


def print_cppm_inline_function_warnings(
    violations: list[tuple[str, int, int]],
    file_path: str,
) -> None:
    path_label = get_path_label(file_path)
    for function_name, start_line, body_lines in violations:
        message = format_cppm_inline_function_message(
            path_label, function_name, start_line, body_lines,
        )
        print(f"⚠️  {message}", file=sys.stderr)
