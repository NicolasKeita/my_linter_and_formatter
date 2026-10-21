#!/usr/bin/env python3
"""
Directory Checks

Checks direct source file (.cpp/.cppm) and subdirectory counts.
"""

import os

MAX_FILES_PER_DIRECTORY = 8
MAX_SUBDIRECTORIES_PER_DIRECTORY = 8
SOURCE_EXTENSIONS = (".cpp", ".cppm")


def count_source_files_per_directory(directories: list[str]) -> dict[str, int]:
    counts = {}
    for directory in directories:
        for root, _, files in os.walk(directory):
            source_count = sum(1 for file in files if file.endswith(SOURCE_EXTENSIONS))
            if source_count > 0:
                counts[root] = counts.get(root, 0) + source_count
    return counts


def check_directory_file_counts(
    directories: list[str],
    max_files: int = MAX_FILES_PER_DIRECTORY,
) -> list[tuple[str, int]]:
    counts = count_source_files_per_directory(directories)
    return sorted((directory, count) for directory, count in counts.items() if count > max_files)


def check_directory_subdirectory_counts(
    directories: list[str],
    max_subdirectories: int = MAX_SUBDIRECTORIES_PER_DIRECTORY,
) -> list[tuple[str, int]]:
    counts = {}
    for directory in directories:
        for root, subdirectories, _ in os.walk(directory):
            if len(subdirectories) > max_subdirectories:
                counts[root] = len(subdirectories)
    return sorted(counts.items())
