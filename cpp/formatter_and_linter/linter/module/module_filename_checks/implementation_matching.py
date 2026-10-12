#!/usr/bin/env python3
"""Match .cpp implementation files against their .cppm module interface."""

import os

from linter.module.module_filename_checks.module_declaration import declared_module

IMPLEMENTATION_EXTENSION = ".cpp"


def declared_modules(directory: str, files: list[str]) -> dict[str, str | None]:
    return {
        file: declared_module(os.path.join(directory, file))
        for file in files
        if file.endswith(IMPLEMENTATION_EXTENSION)
    }


def find_implementation_files(
    files: list[str],
    module_name: str,
    declared: dict[str, str | None],
) -> list[str]:
    candidates = []
    base_name = module_name + IMPLEMENTATION_EXTENSION
    for file in files:
        if not file.endswith(IMPLEMENTATION_EXTENSION):
            continue
        if declared.get(file) == module_name:
            candidates.append(file)
        elif declared.get(file, "missing") is None and (
            file == base_name or file.startswith(module_name + "-")
        ):
            candidates.append(file)
    return sorted(candidates)


def suggest_hyphenated_name(module_name: str, file_name: str) -> str:
    if file_name == module_name + IMPLEMENTATION_EXTENSION:
        return module_name + "-Core" + IMPLEMENTATION_EXTENSION
    return module_name + "-" + file_name[:-len(IMPLEMENTATION_EXTENSION)] + IMPLEMENTATION_EXTENSION
