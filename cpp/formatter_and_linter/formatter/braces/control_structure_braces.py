#!/usr/bin/env python3
"""
Control Structure Brace Formatter

Ensures opening curly braces of control structures (if, else, for, while,
switch, catch, do, try) are placed on the same line as their header.
"""

import re

CONTROL_HEADER_PATTERN = re.compile(r'^\s*(?:if|else|for|while|switch|catch|do|try)\b')


def format_control_structure_braces(code: str) -> str:
    """
    Place the opening brace of control structures (if/else/for/while/switch/
    catch/do/try) on the same line as their header.

    Function definitions, classes, structs, namespaces and enums are left
    untouched (their brace stays on its own line).
    """
    lines = code.splitlines()
    emit = [True] * len(lines)
    total = len(lines)
    i = 0

    while i < total:
        if lines[i].strip() == '{':
            start_idx = _find_statement_start_backward(lines, i)

            if start_idx is not None and CONTROL_HEADER_PATTERN.match(lines[start_idx]):
                target_idx = _last_content_line_before(lines, i)

                if target_idx is not None and target_idx >= start_idx:
                    code_part, comment = _split_trailing_comment(lines[target_idx])
                    lines[target_idx] = _join_brace_with_comment(code_part, comment)
                    emit[i] = False
                    i += 1
                    continue

        i += 1

    return '\n'.join(line for keep, line in zip(emit, lines, strict=False) if keep)


def _join_brace_with_comment(code_part: str, comment: str | None) -> str:
    """Merge a standalone '{' onto its header line, preserving any trailing comment."""
    if comment is not None:
        return code_part + " { " + comment
    return code_part + " {"


def _find_statement_start_backward(lines: list[str], brace_idx: int) -> int | None:
    """
    Walk backward from the standalone '{' at brace_idx to find the first line
    of the statement owning that brace. Returns the line index, or None when
    no consistent statement start can be found.
    """
    balance = 0
    j = brace_idx - 1

    while j >= 0:
        stripped = lines[j].strip()

        if not stripped or stripped.startswith('//'):
            j -= 1
            continue

        balance += stripped.count('(') - stripped.count(')')

        if balance >= 0:
            return j

        j -= 1

    return None


def _last_content_line_before(lines: list[str], brace_idx: int) -> int | None:
    """Return the index of the last non-blank, non-comment line before brace_idx."""
    j = brace_idx - 1

    while j >= 0:
        stripped = lines[j].strip()

        if stripped and not stripped.startswith('//'):
            return j

        j -= 1

    return None


def _split_trailing_comment(line: str) -> tuple[str, str | None]:
    """
    Split a line into (code, comment) where comment is a trailing '//' comment
    (string literals are respected), or None when the line has no comment.
    """
    in_string = False
    string_char = None
    i = 0

    while i < len(line):
        char = line[i]

        if in_string:
            if char == '\\':
                i += 2
                continue
            if char == string_char:
                in_string = False
        elif char == '"' or char == "'":
            in_string = True
            string_char = char
        elif char == '/' and i + 1 < len(line) and line[i + 1] == '/':
            return line[:i].rstrip(), line[i:]

        i += 1

    return line.rstrip(), None
