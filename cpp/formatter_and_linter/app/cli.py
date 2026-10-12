#!/usr/bin/env python3
"""Command-line entry point: argument handling and run loop."""

import sys
from typing import NoReturn

from app.naming import rename_files_to_pascal_case
from app.pipeline import format_file
from app.registry import ProgressBar, file_handler
from app.structure import check_directory_structure

_SEARCH_DIRECTORIES = ("Src", "Tests", "apps")


def _print_usage() -> None:
    print(
        "Usage: python formatter_and_linter.py [-i] [-r/--recursive] <input_file.cpp> ...",
        file=sys.stderr,
    )
    print("       python formatter_and_linter.py --check", file=sys.stderr)
    print("  -i, --in-place    : Modify the file in place (otherwise create output.cpp)", file=sys.stderr)
    print(
        "  -r, --recursive   : Process all .cpp/.cppm files "
        "in Src/, Tests/ and apps/ recursively",
        file=sys.stderr,
    )
    print(
        "  --check           : Check all files in Src/, Tests/ and apps/ "
        "and CMakeLists.txt without modifying",
        file=sys.stderr,
    )


def _collect_search_directories() -> list[str]:
    input_files: list[str] = []
    for directory in _SEARCH_DIRECTORIES:
        input_files += file_handler.find_source_files(directory, include_hpp=False, include_cppm=True)
    return input_files


def _resolve_input_files(
    check_only: bool,
    recursive: bool,
    input_files: list[str],
) -> list[str]:
    if check_only or recursive:
        input_files = _collect_search_directories()
        if not input_files:
            print("No source files found in Src/, Tests/ or apps/", file=sys.stderr)
            sys.exit(1)
        action = "Checking" if check_only else "Found"
        print(f"{action} {len(input_files)} files in Src/, Tests/ and apps/...")
    elif not input_files:
        _print_usage()
        sys.exit(1)
    return input_files


def _process_files(input_files: list[str], in_place: bool, check_only: bool) -> bool:
    has_any_long_lines = False
    progress = ProgressBar(total=len(input_files), interval_sec=1.0)
    progress.start()
    try:
        for input_file in input_files:
            progress.set_file(input_file)
            has_long_lines = progress.run_with_captured_output(
                format_file, input_file, in_place, check_only
            )
            progress.advance()
            if has_long_lines:
                has_any_long_lines = True
    finally:
        progress.stop()
    return has_any_long_lines


def main() -> NoReturn:
    in_place, check_only, recursive, input_files = file_handler.parse_arguments()
    input_files = _resolve_input_files(check_only, recursive, input_files)

    has_directory_violations = check_directory_structure() if (check_only or recursive) else False

    if not check_only and not recursive:
        print("Renaming files to PascalCase...")
        rename_files_to_pascal_case("Src")

    has_any_long_lines = _process_files(input_files, in_place, check_only)

    if has_any_long_lines or has_directory_violations:
        print("[FAIL] Style issues detected!")
    else:
        print("[PASS] All files pass style checks!")

    exit_code = 1 if (has_any_long_lines or has_directory_violations) else 0
    sys.exit(exit_code)
