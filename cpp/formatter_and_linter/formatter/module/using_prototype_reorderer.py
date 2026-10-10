#!/usr/bin/env python3
"""
Using Statement Reordering After Prototypes

Moves top-level using statements after the last top-level import/include/
module declaration or function prototype.
"""

import re

from shared.regex_patterns import USING_REGEX

from formatter.module.prototype_detection import (
    is_function_prototype,
    is_function_prototype_start,
    is_import_or_include_or_module,
)


def _compute_brace_depths(lines: list[str]) -> list[int]:
    """Brace depth at the start of each line, clamped at zero."""
    brace_depths: list[int] = []
    current_depth = 0
    for line in lines:
        brace_depths.append(current_depth)
        for char in line:
            if char == '{':
                current_depth += 1
            elif char == '}':
                current_depth -= 1
                if current_depth < 0:
                    current_depth = 0
    return brace_depths


def _scan_multiline_prototype(lines: list[str], brace_depths: list[int], i: int) -> int | None:
    """Scan a multi-line prototype starting at ``lines[i]``; returns the index
    of its terminating ';' line, or None when a '{' ends the scan instead."""
    j = i + 1
    while j < len(lines) and brace_depths[j] == 0:
        next_stripped = lines[j].strip()
        if next_stripped.endswith(';') and '{' not in next_stripped:
            return j
        if next_stripped.endswith('{') or '{' in next_stripped:
            return None
        j += 1
    return None


class _UsingCollector:
    """Collect the top-level usings and the last import/prototype position."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.brace_depths = _compute_brace_depths(lines)
        self.usings: list[tuple[int, str]] = []
        self.prototype_end_lines: list[int] = []
        self.last_import_pos = -1

    def collect(self) -> None:
        """Walk every line recording usings, prototypes and imports."""
        i = 0
        while i < len(self.lines):
            next_index = None
            if self.brace_depths[i] == 0:
                next_index = self._classify_top_level(i)
            i = next_index if next_index is not None else i + 1

    def _classify_top_level(self, i: int) -> int | None:
        """Classify the top-level line at ``i``; returns the index to resume
        scanning at, or None when the line was not recognised."""
        line = self.lines[i]
        if is_import_or_include_or_module(line):
            self.last_import_pos = i
        elif re.match(USING_REGEX, line):
            self.usings.append((i, line))
        elif is_function_prototype(line):
            self.prototype_end_lines.append(i)
        elif is_function_prototype_start(line):
            prototype_end = _scan_multiline_prototype(self.lines, self.brace_depths, i)
            if prototype_end is None:
                return None
            self.prototype_end_lines.append(prototype_end)
            return prototype_end + 1
        else:
            return None
        return i + 1


def _insertion_pos(collector: _UsingCollector) -> int:
    """Line after which the usings block is re-inserted."""
    last_prototype_pos = max(collector.prototype_end_lines)
    return max(last_prototype_pos, collector.last_import_pos)


def reorder_using_after_prototypes(code: str) -> str:
    lines = code.splitlines()
    collector = _UsingCollector(lines)
    collector.collect()

    if not collector.prototype_end_lines or not collector.usings:
        return code

    insertion_pos = _insertion_pos(collector)
    using_indices = {pos for pos, _ in collector.usings}
    new_lines: list[str] = []
    usings_inserted = False

    for i, line in enumerate(lines):
        if i in using_indices:
            continue
        new_lines.append(line)
        if i == insertion_pos and not usings_inserted:
            new_lines.append('')
            for _, using_line in collector.usings:
                new_lines.append(using_line)
            usings_inserted = True

    return '\n'.join(new_lines)
