#!/usr/bin/env python3
"""Signature detection for .cppm interface function definitions."""

from linter.module.cppm_checks.patterns import (
    CPPM_FUNCTION_SIGNATURE_PATTERN,
    CONTROL_KEYWORDS,
)

SIGNATURE_SCAN_WINDOW = 12


def _scan_signature_bounds(lines: list[str], i: int) -> tuple[list[str], int]:
    signature_lines: list[str] = []
    first_brace_line = -1
    scan_idx = i

    while scan_idx < len(lines) and scan_idx < i + SIGNATURE_SCAN_WINDOW:
        signature_lines.append(lines[scan_idx].strip())
        current_line = lines[scan_idx]

        if ';' in current_line and '{' not in current_line:
            break

        if '{' in current_line:
            first_brace_line = scan_idx
            break

        scan_idx += 1

    return signature_lines, first_brace_line


def _find_body_end_line(lines: list[str], first_brace_line: int) -> int:
    local_depth = 0
    for end_idx in range(first_brace_line, len(lines)):
        local_depth += lines[end_idx].count('{')
        local_depth -= lines[end_idx].count('}')
        if local_depth == 0:
            return end_idx
    return -1


def detect_definition(lines: list[str], i: int) -> tuple[object, int, int] | None:
    """Return (signature_match, first_brace_line, end_line) for a def at line i."""
    if '(' not in lines[i]:
        return None

    signature_lines, first_brace_line = _scan_signature_bounds(lines, i)
    if first_brace_line == -1:
        return None

    normalized_signature = ' '.join(signature_lines)
    signature_match = CPPM_FUNCTION_SIGNATURE_PATTERN.match(normalized_signature)
    if not signature_match:
        return None

    function_name = signature_match.group(1).split('::')[-1]
    if function_name in CONTROL_KEYWORDS:
        return None

    end_line = _find_body_end_line(lines, first_brace_line)
    if end_line == -1:
        return None

    return signature_match, first_brace_line, end_line
