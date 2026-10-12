#!/usr/bin/env python3
"""Character-level cleaning: normalize spaces and strip trailing whitespace."""

from formatter.spacing.prototype_spacing.patterns import NON_BREAKING_SPACE_CHARS


def normalize_characters(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        for char in NON_BREAKING_SPACE_CHARS:
            line = line.replace(char, " ")
        cleaned.append(line.rstrip())
    return cleaned
