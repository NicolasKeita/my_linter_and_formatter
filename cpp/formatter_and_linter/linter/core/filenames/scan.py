"""Collect the C++ structure scope and preserve declared module prefixes."""

import os
from pathlib import Path

from linter.core.filenames import find_similar
from linter.core.filenames.ownership import module_prefix


def check_similar_filenames(directories: list[str], scope: str = "directory") -> list[tuple[Path, str]]:
    files = sorted(
        {
            (Path(root) / name).resolve()
            for directory in directories
            for root, _, names in os.walk(directory)
            for name in names
            if Path(name).suffix in {".cpp", ".cppm"}
        }
    )
    interfaces = [path for path in files if path.suffix == ".cppm"]
    modules = {path: module_prefix(path, interfaces) for path in files}
    return find_similar(files, scope, modules)
