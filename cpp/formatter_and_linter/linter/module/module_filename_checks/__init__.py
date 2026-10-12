#!/usr/bin/env python3
"""
Module Filename Checks

Checks the naming convention between module interfaces (.cppm) and their
implementation files (.cpp):

- A single implementation file must be exactly '<ModuleName>.cpp'.
- A missing implementation file is not reported here: the inline function
  body check ([WARN_CPPM_INLINE_FUNCTION]) already indicates when an
  implementation .cpp file is needed.
- Multiple implementation files must all follow '<ModuleName>-<Suffix>.cpp'
  and none may be the plain '<ModuleName>.cpp'.
- A file is an implementation of '<ModuleName>' only when it actually
  declares 'module <ModuleName>;' inside its content. Files that merely
  import the module or share a filename prefix (e.g. 'HilRunnerMain.cpp'
  importing 'HilRunner') are consumers, not implementations.
- Files without any module declaration (e.g. empty files) fall back to
  filename matching: exactly '<ModuleName>.cpp' or '<ModuleName>-*.cpp'.
"""

import os

from linter.module.module_filename_checks.implementation_matching import (
    IMPLEMENTATION_EXTENSION,
    declared_modules,
    find_implementation_files,
    suggest_hyphenated_name,
)

INTERFACE_EXTENSION = ".cppm"


def _single_implementation_violation(root: str, module_name: str, implementation: str):
    expected_name = module_name + IMPLEMENTATION_EXTENSION
    if implementation == expected_name:
        return None
    return (
        os.path.join(root, implementation),
        "single implementation of '" + module_name + "' must be named '"
        + expected_name + "'",
    )


def _multiple_implementation_violations(
    root: str,
    module_name: str,
    implementations: list[str],
) -> list[tuple[str, str]]:
    base_name = module_name + IMPLEMENTATION_EXTENSION
    violations = []
    for file_name in implementations:
        if file_name == base_name or not file_name.startswith(module_name + "-"):
            suggestion = suggest_hyphenated_name(module_name, file_name)
            violations.append((
                os.path.join(root, file_name),
                "multiple implementations of '" + module_name + "' must follow '"
                + module_name + "-<Suffix>.cpp' (e.g. '" + suggestion + "')",
            ))
    return violations


def _validate_interface(
    root: str,
    files: list[str],
    interface_file: str,
    declared: dict[str, str | None],
) -> list[tuple[str, str]]:
    module_name = interface_file[:-len(INTERFACE_EXTENSION)]
    implementations = find_implementation_files(files, module_name, declared)

    if len(implementations) == 0:
        return []
    if len(implementations) == 1:
        violation = _single_implementation_violation(root, module_name, implementations[0])
        return [violation] if violation else []

    return _multiple_implementation_violations(root, module_name, implementations)


def check_module_filename_convention(directories: list[str]) -> list[tuple[str, str]]:
    """
    Validate module interface / implementation filename consistency.

    Returns violations as (file_path, message) tuples sorted by path.
    """
    violations: list[tuple[str, str]] = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            interface_files = [
                file for file in files if file.endswith(INTERFACE_EXTENSION)
            ]
            declared = declared_modules(root, files)
            for interface_file in interface_files:
                violations.extend(
                    _validate_interface(root, files, interface_file, declared)
                )

    return sorted(violations)


__all__ = ["check_module_filename_convention"]
