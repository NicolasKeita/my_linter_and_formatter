"""Find direct filename matches and produce one diagnostic per affected file."""

import os
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from .comparison import reason
from .identity import name_parts


def find_similar(
    files: list[Path], scope: str = "directory", modules: dict[Path, str] | None = None
) -> list[tuple[Path, str]]:
    if scope not in {"directory", "project"}:
        raise ValueError("similarity scope must be directory or project")
    groups: dict[tuple[str, str], list[Path]] = defaultdict(list)
    matches: dict[Path, list[str]] = defaultdict(list)
    for path in sorted({path.resolve() for path in files}):
        groups[(str(path.parent) if scope == "directory" else "", name_parts(path.name)[1])].append(path)
    for group in groups.values():
        for left, right in combinations(group, 2):
            if left.parent != right.parent and left.name == right.name:
                continue
            module = (modules or {}).get(left, "")
            if module != (modules or {}).get(right, ""):
                module = ""
            message = reason(left.name, right.name, module)
            if message:
                matches[left].append(f"{os.path.relpath(right, left.parent)} ({message})")
                matches[right].append(f"{os.path.relpath(left, right.parent)} ({message})")
    return [
        (path, "Similar filename(s): " + "; ".join(sorted(peers)) + ". Prefer responsibility-based names.")
        for path, peers in sorted(matches.items())
    ]
