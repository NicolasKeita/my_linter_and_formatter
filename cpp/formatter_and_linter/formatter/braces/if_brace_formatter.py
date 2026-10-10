#!/usr/bin/env python3
"""
Short If Statement Formatter (With Braces)

Formats if statements that have braces but are still written on a single
line, splitting the condition and each statement onto their own lines.
"""

import re


def _toggle_string_state(char: str, in_string: bool, string_char: str | None) -> tuple[bool, str | None]:
    """Track whether a quote character opens, closes, or leaves a string literal."""
    if in_string:
        if char == string_char:
            return False, None
        return True, string_char
    return True, char


def _is_escaped(line: str, pos: int) -> bool:
    return pos > 0 and line[pos - 1] == "\\"


def find_matching_paren(line: str, opening_pos: int) -> int:
    """
    Find the position of the closing parenthesis that matches the opening one.
    Handles nested parentheses correctly.

    Args:
        line: The code line
        opening_pos: Position of the opening parenthesis

    Returns:
        Position of matching closing parenthesis, or -1 if not found
    """
    if opening_pos < 0 or opening_pos >= len(line) or line[opening_pos] != "(":
        return -1

    paren_depth = 0
    in_string = False
    string_char = None

    for i in range(opening_pos, len(line)):
        char = line[i]

        if char in ('"', "'") and not _is_escaped(line, i):
            in_string, string_char = _toggle_string_state(char, in_string, string_char)

        if not in_string:
            if char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
                if paren_depth == 0:
                    return i

    return -1


def _split_braced_statements(line: str) -> tuple[str, list[str], str] | None:
    """Split a single-line braced if into (condition, statements, indent)."""
    if_brace_pattern = r"^\s*if\s*\([^)]+\)\s*\{[^}]+\}\s*$"
    if not re.match(if_brace_pattern, line):
        return None
    condition_match = re.search(r"if\s*\(([^)]+)\)", line)
    if not condition_match:
        return None
    brace_start = line.find("{") + 1
    brace_end = line.rfind("}")
    content = line[brace_start:brace_end].strip()
    statements = [part.strip() for part in content.split(";") if part.strip()]
    indent_match = re.match(r"^(\s*)", line)
    leading_whitespace = indent_match.group(1) if indent_match else ""
    return condition_match.group(1), statements, leading_whitespace


def _emit_braced_if(condition: str, statements: list[str], indent: str) -> list[str]:
    inner_indent = indent + "    "
    emitted = [f"{indent}if ({condition}) {{"]
    emitted.extend(f"{inner_indent}{statement};" for statement in statements if statement)
    emitted.append(f"{indent}}}")
    return emitted


def format_short_if_statements_with_braces(code: str) -> str:
    """
    Format if statements that have braces but are still on a single line.

    Args:
        code: The code as a string to format

    Returns:
        The formatted code with properly formatted if statements
    """
    lines = code.splitlines()
    formatted_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        split = _split_braced_statements(line)

        if split is not None:
            condition, statements, leading_whitespace = split
            formatted_lines.extend(_emit_braced_if(condition, statements, leading_whitespace))
        else:
            formatted_lines.append(line)

        i += 1

    return "\n".join(formatted_lines)
