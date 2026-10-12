#!/usr/bin/env python3
"""Project-level structural checks (directories, modules, CMake)."""

from app.registry import linter


def check_directory_structure() -> bool:
    directory_violations = linter.check_directory_file_counts(
        ["Src", "Tests", "apps"],
        max_files=linter.MAX_FILES_PER_DIRECTORY,
    )
    linter.print_directory_file_count_warnings(
        directory_violations,
        linter.MAX_FILES_PER_DIRECTORY,
    )

    module_filename_violations = linter.check_module_filename_convention(["Src", "Tests", "apps"])
    linter.print_module_filename_warnings(module_filename_violations)

    module_size_violations = linter.check_module_implementation_counts(["Src", "Tests", "apps"])
    linter.print_module_size_warnings(module_size_violations)

    cmake_length_violations = linter.check_cmake_file_lengths(["Src", "Tests", "apps"])
    linter.print_cmake_length_warnings(
        cmake_length_violations,
        linter.MAX_CMAKELISTS_LINES,
    )

    return (
        len(directory_violations) > 0
        or len(module_filename_violations) > 0
        or len(module_size_violations) > 0
        or len(cmake_length_violations) > 0
    )
