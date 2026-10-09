#!/usr/bin/env python3
"""
Detection of the stream insertion/extraction operators on a single line.

Function signatures never contain '<<' or '>>', so lines carrying them are
statement continuations (e.g. multi-line std::cout chains) and must not be
treated as function declaration headers. Scanning skips string and character
literals.
"""


def _opens_literal(char: str) -> bool:
    return char == '"' or char == "'"


def _ends_literal(char: str, string_char: str) -> bool:
    return char == string_char


def has_stream_operators(line: str) -> bool:
    """Return True when the line has '<<' or '>>' outside string literals."""
    in_string = False
    string_char = None
    i = 0

    while i < len(line):
        char = line[i]

        if in_string:
            if char == "\\":
                i += 2
                continue
            if _ends_literal(char, string_char):
                in_string = False
        elif _opens_literal(char):
            in_string = True
            string_char = char
        elif char == "<" and line[i : i + 2] == "<<":
            return True
        elif char == ">" and line[i : i + 2] == ">>":
            return True

        i += 1

    return False
