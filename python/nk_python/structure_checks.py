"""Collect Python files and check direct file and subdirectory counts."""

import os
from fnmatch import fnmatchcase
from pathlib import Path

from .model import Issue

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".cache",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv*",
    ".vs",
    "*.egg-info",
    "venv",
    "__pycache__",
    "bin",
    "build",
    "cmake-build-*",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "obj",
}
SUFFIXES = {".py", ".pyi"}
MAX_SUBDIRECTORIES = 8


def discover(paths: list[Path], max_files: int = 8) -> tuple[list[Path], list[Issue]]:
    files: set[Path] = set()
    issues: list[Issue] = []
    seen_directories: set[Path] = set()
    for target in paths:
        target = target.resolve()
        if not target.exists():
            raise FileNotFoundError(target)
        if target.is_file():
            if target.suffix not in SUFFIXES:
                raise ValueError(f"Unsupported source file: {target}")
            files.add(target)
            continue
        for root, directory_names, file_names in os.walk(target):
            directory_names[:] = sorted(
                name
                for name in directory_names
                if not any(fnmatchcase(name, pattern) for pattern in IGNORED_DIRECTORIES)
            )
            directory = Path(root).resolve()
            source_names = sorted(name for name in file_names if Path(name).suffix in SUFFIXES)
            files.update(directory / name for name in source_names)
            if directory not in seen_directories and len(source_names) > max_files:
                issues.append(
                    Issue(directory, 1, "PY008", f"Directory has {len(source_names)} Python files (max {max_files}).")
                )
            if directory not in seen_directories and len(directory_names) > MAX_SUBDIRECTORIES:
                issues.append(
                    Issue(
                        directory,
                        1,
                        "PY009",
                        f"Directory has {len(directory_names)} direct subdirectories (max {MAX_SUBDIRECTORIES}).",
                    )
                )
            seen_directories.add(directory)
    return sorted(files), sorted(issues)
