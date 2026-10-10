#!/usr/bin/env python3
"""Classification of a masked code line as a local variable declaration."""

from .scanning import _COMPOUND_ASSIGN_RE, _NON_DECLARATION_KEYWORD_RE


def _find_head(line: str) -> str:
    """
    Return the part of the line before the first top-level '=' (standalone,
    not comparison or compound assignment), '{' or ';'. Parenthesis depth is
    tracked so that '=' or '{' inside function calls or nested initializers
    are ignored.
    """
    depth = 0
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        if char == '(':
            depth += 1
        elif char == ')':
            if depth > 0:
                depth -= 1
        elif depth == 0:
            if char == '=':
                if i + 1 < length and line[i + 1] == '=':
                    i += 2
                    continue
                if i > 0 and line[i - 1] in '!<>':
                    i += 1
                    continue
                return line[:i].strip()
            if char == '{':
                return line[:i].strip()
            if char == ';':
                return line[:i].strip()
        i += 1
    return line.strip()


def _is_declaration_line(masked_stripped: str) -> bool:
    """
    Check whether a code line (strings/comments already masked, whitespace
    stripped) is a local variable declaration or initialisation.
    """
    if _NON_DECLARATION_KEYWORD_RE.match(masked_stripped):
        return False

    if '<<' in masked_stripped or '>>' in masked_stripped:
        return False

    if _COMPOUND_ASSIGN_RE.search(masked_stripped):
        return False

    head = _find_head(masked_stripped)
    tokens = head.split()
    if len(tokens) < 2:
        return False

    first_token = tokens[0]
    if '.' in first_token or '[' in first_token or '(' in first_token:
        return False

    return True
