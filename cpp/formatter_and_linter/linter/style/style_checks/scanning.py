#!/usr/bin/env python3
"""Low-level line scanning helpers: masking and declaration classification."""

import re

_NON_DECLARATION_KEYWORD_RE = re.compile(
    r'^(?:return|throw|break|continue|goto|case|default|'
    r'delete|new|sizeof|static_assert|'
    r'using|typedef|namespace|class|struct|enum|union|'
    r'import|module|'
    r'if|for|while|switch|catch|else|do|try)\b'
)

_COMPOUND_ASSIGN_RE = re.compile(r'(?:[-+*/%&|^]=|<<=|>>=)')


def _mask_string_literal(line: str, i: int, masked: list[str]) -> int:
    """Mask a string/char literal starting at index ``i``; return the next index."""
    length = len(line)
    quote = line[i]
    masked.append(' ')
    i += 1
    while i < length:
        if line[i] == '\\':
            masked.append('  ')
            i += 2
            continue
        masked.append(' ')
        i += 1
        if line[i - 1] == quote:
            break
    return i


def _mask_line_comment_or_block_start(line: str, i: int, length: int, masked: list[str]) -> tuple[bool, bool, int]:
    """Handle '//' and '/*' at index ``i``.

    Returns (is_comment, in_block_comment, next_index). ``is_comment`` is True
    when a line comment was found (the rest of the line is already masked).
    """
    if line[i] == '/' and i + 1 < length and line[i + 1] == '/':
        masked.append(' ' * (length - i))
        return True, False, length
    if line[i] == '/' and i + 1 < length and line[i + 1] == '*':
        masked.append('  ')
        return False, True, i + 2
    return False, False, i


def _mask_block_comment_char(line: str, i: int, length: int, masked: list[str]) -> tuple[bool, int]:
    """Mask one char while inside a block comment; return (in_block_comment, next_index)."""
    if line[i] == '*' and i + 1 < length and line[i + 1] == '/':
        masked.append('  ')
        return False, i + 2
    masked.append(' ')
    return True, i + 1


def _mask_strings_and_comments(line: str, in_block_comment: bool) -> tuple[str, bool]:
    """
    Replace string literals, character literals and comments with spaces so
    brace and parenthesis tracking only sees code characters. Returns the
    masked line and the updated block-comment state for multi-line comments.
    """
    masked: list[str] = []
    i = 0
    length = len(line)

    while i < length:
        char = line[i]

        if in_block_comment:
            in_block_comment, i = _mask_block_comment_char(line, i, length, masked)
            continue

        if char == '/':
            is_comment, in_block_comment, next_i = _mask_line_comment_or_block_start(
                line, i, length, masked
            )
            if is_comment:
                break
            if next_i == i:
                masked.append(char)
                i += 1
                continue
            i = next_i
            continue

        if char == '"' or char == "'":
            i = _mask_string_literal(line, i, masked)
            continue

        masked.append(char)
        i += 1

    return ''.join(masked), in_block_comment


def _find_matching_paren(text: str) -> int | None:
    """
    Return the index of the opening parenthesis matching the closing
    parenthesis at the end of the text, or None when unbalanced.
    """
    depth = 0
    for i in range(len(text) - 1, -1, -1):
        char = text[i]
        if char == ')':
            depth += 1
        elif char == '(':
            depth -= 1
            if depth == 0:
                return i
    return None
