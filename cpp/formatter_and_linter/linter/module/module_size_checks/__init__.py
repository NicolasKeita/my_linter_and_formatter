#!/usr/bin/env python3
"""
Module Size Checks

Warns when a module or functional namespace accumulates too many
implementation files, mirroring the single responsibility principle applied
at module scale.

Source files (.cpp / .cppm) are grouped by their C++20 module declaration
('module <Name>;' or 'export module <Name>;'): every implementation file
belongs to the module it declares, whatever its filename functional prefix is
(e.g. 'SilObservabilityTelemetry-*.cpp' declaring 'module SilScenarios;'
counts for 'SilScenarios'). Partition suffixes ('module <Name>:<Part>;') are
folded into the base module name. Files without any module declaration fall
back to their filename functional prefix (e.g. 'Alpha-Beta-*' groups as
'Alpha-Beta'). Only implementation files (.cpp) are counted, and when a group
exceeds the threshold a warning suggests splitting it into sub-modules.
"""

from linter.module.module_size_checks.grouping import (
    build_group_tree,
    subtree_implementation_count,
)
from linter.module.module_size_checks.messages import (
    MAX_IMPLEMENTATION_FILES_PER_MODULE,
    SUB_MODULE_PLACEHOLDER,
    format_module_too_large_message,
)


def _make_suggestion_label(label: str, children: dict[str, dict]) -> str:
    if children:
        return label + "::" + min(children)
    return label + "::" + SUB_MODULE_PLACEHOLDER


def _collect_exceeding_groups(
    node: dict,
    segments: list[str],
    max_files: int,
    violations: list[tuple[str, int, str]],
) -> None:
    total = subtree_implementation_count(node)
    if total > max_files and not any(
        subtree_implementation_count(child) > max_files
        for child in node["children"].values()
    ):
        label = "::".join(segments)
        violations.append((
            label,
            total,
            _make_suggestion_label(label, node["children"]),
        ))
        return

    for key, child in node["children"].items():
        _collect_exceeding_groups(child, segments + [key], max_files, violations)


def check_module_implementation_counts(
    directories: list[str],
    max_files: int = MAX_IMPLEMENTATION_FILES_PER_MODULE,
) -> list[tuple[str, int, str]]:
    """
    Report groups holding more than max_files implementation (.cpp) files as
    (label, implementation_count, suggestion_label) tuples sorted by label.
    """
    tree = build_group_tree(directories)
    violations: list[tuple[str, int, str]] = []
    for key, node in tree["children"].items():
        _collect_exceeding_groups(node, [key], max_files, violations)
    return sorted(violations)


__all__ = [
    "MAX_IMPLEMENTATION_FILES_PER_MODULE",
    "format_module_too_large_message",
    "check_module_implementation_counts",
]
