"""Recognize C++ module names and interface-backed filename prefixes."""

import re
from pathlib import Path

from linter.style.style_checks import _mask_strings_and_comments

DECLARATION = re.compile(
    r"^\s*(?:export\s+)?module\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
    r"(?::[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)?\s*;"
)


def module_prefix(path: Path, interfaces: list[Path]) -> str:
    in_comment = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        masked, in_comment = _mask_strings_and_comments(line, in_comment)
        match = DECLARATION.match(masked)
        if match:
            return match[1]
    candidates = [item.stem for item in interfaces if item.parent == path.parent]
    for name in sorted(candidates, key=lambda value: (-len(value), value)):
        if path.stem.startswith(name + "-"):
            return name
    return ""
