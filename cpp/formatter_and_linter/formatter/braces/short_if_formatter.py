#!/usr/bin/env python3
"""
Short If Statement Formatter

A formatter that ensures if statements are not placed on a single line,
following the coding style rule: AllowShortIfStatementsOnASingleLine: false.
Handles both simple if statements and if statements with braces on single lines.

The with-braces handling lives in if_brace_formatter.
"""

import re

from formatter.braces.if_brace_formatter import (
    find_matching_paren,
    format_short_if_statements_with_braces,
)


def _leading_indent(line: str) -> str:
    indent_match = re.match(r"^(\s*)", line)
    return indent_match.group(1) if indent_match else ""


def _expand_single_line_if(line: str, closing_paren_pos: int) -> list[str] | None:
    """Expand 'if (cond) statement;' into a braced block, or None when no expansion applies."""
    after_condition = line[closing_paren_pos + 1 :].strip()
    if not after_condition or after_condition.startswith("{"):
        return None
    if_part = line[: closing_paren_pos + 1]
    statement = after_condition.rstrip(";").strip()
    leading_whitespace = _leading_indent(line)
    inner_indent = leading_whitespace + "    "
    return [
        f"{if_part} {{",
        f"{inner_indent}{statement};",
        f"{leading_whitespace}}}",
    ]


def format_short_if_statements(code: str) -> str:
    """
    Format if statements to ensure they are not on a single line.
    Only format if statements that have code ON THE SAME LINE as the condition.
    Allow instructions after if without brackets if they are on the next line (no changes needed).

    Args:
        code: The code as a string to format

    Returns:
        The formatted code with if statements properly split across lines
    """
    lines = code.splitlines()
    formatted_lines = []

    for line in lines:
        if_match = re.search(r"^\s*if\s*\(", line)

        if if_match:
            opening_paren_pos = if_match.end() - 1
            closing_paren_pos = find_matching_paren(line, opening_paren_pos)

            if closing_paren_pos != -1:
                expanded = _expand_single_line_if(line, closing_paren_pos)
                if expanded is not None:
                    formatted_lines.extend(expanded)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)


def _without_braces(code: str) -> str:
    return format_short_if_statements(code)


def _with_braces(code: str) -> str:
    return format_short_if_statements_with_braces(code)


def format_if_statements(code: str) -> str:
    """
    Main function to format all types of short if statements.

    Args:
        code: The code as a string to format

    Returns:
        The formatted code with all if statements properly formatted
    """
    return _with_braces(_without_braces(code))


__all__ = [
    "find_matching_paren",
    "format_short_if_statements",
    "format_short_if_statements_with_braces",
    "format_if_statements",
]


if __name__ == "__main__":
    test_code = """#include <iostream>

int main() {
    int x = 5;
    if (x > 0) return x;
    if (x < 0) { std::cout << "negative"; }
    if (x == 5) std::cout << "five";
    return 0;
}"""

    print("Original code:")
    print(test_code)
    print("\nFormatted code:")
    print(format_if_statements(test_code))
