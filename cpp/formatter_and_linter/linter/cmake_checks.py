#!/usr/bin/env python3
"""
CMake Checks

Checks the CMakeLists.txt files of the project and reports the ones that
exceed the maximum line count and should be split into smaller CMake files.
"""

import os

MAX_CMAKELISTS_LINES = 300
CMAKELISTS_FILENAME = "CMakeLists.txt"


def find_cmake_files(directories: list[str]) -> list[str]:
    cmake_files = set()
    if os.path.isfile(CMAKELISTS_FILENAME):
        cmake_files.add(CMAKELISTS_FILENAME)
    for directory in directories:
        for root, _, files in os.walk(directory):
            if CMAKELISTS_FILENAME in files:
                cmake_files.add(os.path.join(root, CMAKELISTS_FILENAME))
    return sorted(cmake_files)


def count_file_lines(file_path: str) -> int:
    with open(file_path, encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def check_cmake_file_lengths(
    directories: list[str],
    max_lines: int = MAX_CMAKELISTS_LINES,
) -> list[tuple[str, int]]:
    violations: list[tuple[str, int]] = []
    for file_path in find_cmake_files(directories):
        line_count = count_file_lines(file_path)
        if line_count > max_lines:
            violations.append((file_path, line_count))
    return violations
