#!/usr/bin/env python3
"""
Walking upwards from a body brace to the line that starts the function.

Continuation lines (blank, comment-only, '{', '}', initialiser list members and
stream continuations) are skipped; the first remaining line is the signature
line, and the signature may itself span several lines.
"""

from shared.brace_utils import extract_function_name
from shared.function_analysis.qualifiers import strip_trailing_qualifiers
from shared.function_analysis.stream_operators import has_stream_operators

SKIPPABLE_LINE_PREFIXES = (":", ",")
SKIPPABLE_EXACT_LINES = ("{", "}")


def _skip_continuation_line(line: str) -> bool:
    if not line or line.startswith("//"):
        return True
    if line in SKIPPABLE_EXACT_LINES:
        return True
    if line.startswith(SKIPPABLE_LINE_PREFIXES):
        return True
    return has_stream_operators(line)


def _opens_signature(line: str) -> bool:
    return strip_trailing_qualifiers(line).endswith(")")


def _match_signature_start(lines: list[str], line_idx: int) -> int | None:
    """Return the index of the line holding the signature's opening paren."""
    effective_line = strip_trailing_qualifiers(lines[line_idx])
    paren_depth = 1
    for char in reversed(effective_line[:-1]):
        if char == ")":
            paren_depth += 1
        elif char == "(":
            paren_depth -= 1
            if paren_depth == 0:
                return line_idx
    for candidate in range(line_idx - 1, -1, -1):
        for char in reversed(lines[candidate]):
            if char == ")":
                paren_depth += 1
            elif char == "(":
                paren_depth -= 1
                if paren_depth == 0:
                    return candidate
    return None


def find_function_start_for_brace(lines: list[str], line_idx: int) -> int | None:
    """Return the index of the first line of the function owning this brace."""
    for i in range(line_idx - 1, -1, -1):
        line = lines[i].strip()
        if _skip_continuation_line(line):
            continue
        if not _opens_signature(line):
            return None
        signature_line = _match_signature_start(lines, i)
        if signature_line is None:
            return None
        if extract_function_name(lines[signature_line]) is not None:
            return signature_line
        return None
    return None
