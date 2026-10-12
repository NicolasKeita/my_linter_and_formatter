#!/usr/bin/env python3
"""
Module Interface (.cppm) Checks

Detects non-trivial function implementations inside .cppm module interfaces;
implementations belong in .cpp files.
"""

import re

from linter.module.cppm_checks.detector import detect_definition
from linter.module.cppm_checks.patterns import (
    CLASS_DECLARATION_REGEX,
    MAX_CPPM_INLINE_BODY_LINES,
)
from linter.module.cppm_checks.scanning import (
    build_line_depths,
    count_significant_body_lines,
)


def check_cppm_interface_implementations(
    code: str,
    max_body_lines: int = MAX_CPPM_INLINE_BODY_LINES
) -> list[tuple[str, int, int]]:
    lines = code.splitlines()
    if not any(CLASS_DECLARATION_REGEX.search(line) for line in lines):
        return []

    line_depths = build_line_depths(lines)
    violations: list[tuple[str, int, int]] = []

    i = 0
    while i < len(lines):
        if line_depths[i] != 0:
            i += 1
            continue

        detected = detect_definition(lines, i)
        if detected is None:
            i += 1
            continue

        signature_match, first_brace_line, end_line = detected
        significant_lines = count_significant_body_lines(lines, first_brace_line, end_line)
        if significant_lines > max_body_lines:
            full_name = signature_match.group(1)
            violations.append((full_name, i + 1, significant_lines))

        i = end_line + 1

    return violations


__all__ = ["MAX_CPPM_INLINE_BODY_LINES", "check_cppm_interface_implementations"]
