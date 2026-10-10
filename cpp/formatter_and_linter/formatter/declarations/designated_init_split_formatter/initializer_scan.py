#!/usr/bin/env python3
"""Locating the outermost braced initializer of a single-line statement."""

_TYPE_KEYWORDS = frozenset({"struct", "class", "enum", "union", "namespace"})


def _semicolon_after(line: str, start: int) -> int:
    """
    Return the index of the first character of ``line`` at or after ``start``
    when it is a semicolon, -1 otherwise.
    """
    index = start
    while index < len(line) and line[index] in " \t":
        index += 1
    if index < len(line) and line[index] == ";":
        return index
    return -1


def _name_column_before(line: str, open_index: int) -> int:
    """
    Return the column of the identifier written just before the opening brace
    at ``open_index`` (optional spaces allowed between both), -1 when there is
    no such identifier (lambda, call argument, template closing bracket, ...)
    or when the identifier names a type being defined (struct / class / enum /
    union / namespace).
    """
    end = open_index
    while end > 0 and line[end - 1] in " \t":
        end -= 1
    start = end
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1
    if start == end:
        return -1
    previous = line[start - 1] if start > 0 else ""
    if previous == "" or previous in ".:>":
        return -1
    word_start = start
    while word_start > 0 and (line[word_start - 1].isalnum() or line[word_start - 1] == "_"):
        word_start -= 1
    if line[word_start:start] in _TYPE_KEYWORDS:
        return -1
    return start


def _scan_brace_pair(line: str) -> tuple[tuple[int, int] | None, bool]:
    """
    Scan ``line`` for the outermost top-level brace pair, skipping string
    literals, escapes and ``//`` line comments. Returns ``(pair, broken)``
    where ``pair`` is ``(open_index, close_index)`` or None and ``broken`` is
    True when the line ends inside a string or with unbalanced brackets.
    """
    stack: list[tuple[str, int]] = []
    last_brace_pair: tuple[int, int] | None = None
    in_string = False
    string_char = ""
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        if in_string:
            if char == "\\":
                i += 2
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
        if char == "/" and i + 1 < length and line[i + 1] == "/":
            break
        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue
        if char in "([{":
            stack.append((char, i))
        elif char in ")]}":
            if not stack:
                return None, True
            open_char, open_index = stack.pop()
            if open_char == "{" and not stack:
                last_brace_pair = (open_index, i)
        i += 1
    return last_brace_pair, in_string or bool(stack)


def _find_initializer(line: str) -> tuple[int, int, int, int] | None:
    """
    Locate the outermost braced initializer of a single-line statement.

    Returns (open_index, close_index, name_column, semicolon_index) when the
    line has the shape '<prefix><name>{...};' (a trailing line comment after
    the semicolon is allowed), otherwise None.
    """
    last_brace_pair, broken = _scan_brace_pair(line)
    if broken or last_brace_pair is None:
        return None
    open_index, close_index = last_brace_pair
    semicolon_index = _semicolon_after(line, close_index + 1)
    if semicolon_index == -1:
        return None
    name_column = _name_column_before(line, open_index)
    if name_column == -1:
        return None
    return (open_index, close_index, name_column, semicolon_index)
