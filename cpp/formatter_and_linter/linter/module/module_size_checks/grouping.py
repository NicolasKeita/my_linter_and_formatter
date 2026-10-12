#!/usr/bin/env python3
"""Group source files into module/namespace trees for size checks."""

import os
import re

from linter.style.style_checks import _mask_strings_and_comments

SOURCE_EXTENSIONS = ('.cpp', '.cppm')
IMPLEMENTATION_EXTENSION = '.cpp'

_MODULE_DECLARATION_RE = re.compile(
    r"^\s*(?:export\s+)?module\s+([A-Za-z_]\w*(?::[A-Za-z_]\w*)*)\s*;"
)


def _read_file_text(file_path: str) -> str:
    with open(file_path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _extract_module_declaration_name(content: str) -> str | None:
    in_block_comment = False
    for line in content.splitlines():
        masked_line, in_block_comment = _mask_strings_and_comments(line, in_block_comment)
        match = _MODULE_DECLARATION_RE.match(masked_line)
        if match:
            return match.group(1).split(":")[0]
    return None


def _resolve_group_segments(file_path: str, file_name: str) -> list[str]:
    module_name = _extract_module_declaration_name(_read_file_text(file_path))
    if module_name:
        return [module_name]
    stem = os.path.splitext(file_name)[0]
    segments = stem.split("-")
    if len(segments) >= 2:
        return segments[:-1]
    return [stem]


def build_group_tree(directories: list[str]) -> dict[str, dict]:
    tree: dict[str, dict] = {"count": 0, "children": {}}
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file_name in sorted(files):
                if not file_name.endswith(SOURCE_EXTENSIONS):
                    continue
                segments = _resolve_group_segments(os.path.join(root, file_name), file_name)
                node = tree
                for segment in segments:
                    node = node["children"].setdefault(segment, {"count": 0, "children": {}})
                if file_name.endswith(IMPLEMENTATION_EXTENSION):
                    node["count"] += 1
    return tree


def subtree_implementation_count(node: dict) -> int:
    total = node["count"]
    for child in node["children"].values():
        total += subtree_implementation_count(child)
    return total
