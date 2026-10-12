#!/usr/bin/env python3
"""Top-level entry point combining character and blank-line cleaning."""

from formatter.spacing.prototype_spacing.character_cleaning import normalize_characters
from formatter.spacing.prototype_spacing.collapser import collapse_prototype_blank_lines


def clean_code(code: str) -> str:
    had_trailing_newline = code.endswith("\n")
    lines = code.splitlines()
    lines = normalize_characters(lines)
    lines = collapse_prototype_blank_lines(lines)
    cleaned = "\n".join(lines)
    if cleaned and had_trailing_newline:
        cleaned += "\n"
    return cleaned

