#!/usr/bin/env python3
"""Multi-line signature scanning: locate a function definition's opening brace."""

from shared.brace_utils import extract_function_name
from shared.function_analysis import strip_trailing_qualifiers

from .scanning import _find_matching_paren, _mask_strings_and_comments

MAX_SIGNATURE_SCAN_LINES = 50


def _classify_signature(
    signature_parts: list[str],
    start_line: int | None,
    line_idx: int,
) -> tuple[str, tuple[str, int] | None]:
    """
    Classify the accumulated signature text as 'found' (function definition,
    result carries the name and start line), 'invalid' (balanced parentheses
    but no function name, e.g. a control structure) or 'incomplete' (the
    parameter list is not balanced yet and more lines must be accumulated).
    """
    signature = ' '.join(signature_parts)
    if not signature:
        return ('incomplete', None)
    effective_signature = strip_trailing_qualifiers(signature)
    if not effective_signature.endswith(')'):
        return ('incomplete', None)
    paren_index = _find_matching_paren(effective_signature)
    if paren_index is None:
        return ('incomplete', None)
    func_name = extract_function_name(effective_signature[:paren_index] + '(')
    if func_name is None:
        return ('invalid', None)
    return ('found', (func_name, start_line if start_line is not None else line_idx))


def _scan_previous_lines(
    lines: list[str],
    line_idx: int,
    signature_parts: list[str],
    start_line: int | None,
) -> tuple[str, tuple[str, int] | None]:
    """Walk backwards accumulating signature lines until classified or exhausted."""
    scan_idx = line_idx - 1
    while scan_idx >= 0 and len(signature_parts) < MAX_SIGNATURE_SCAN_LINES:
        masked_line, _ = _mask_strings_and_comments(lines[scan_idx], False)
        stripped_line = masked_line.strip()
        if (not stripped_line
                or stripped_line.startswith('#')
                or stripped_line.startswith(':')
                or stripped_line.startswith(',')):
            scan_idx -= 1
            continue
        if stripped_line == '{' or stripped_line == '}' or stripped_line.endswith(';'):
            return ('invalid', None)

        signature_parts.insert(0, stripped_line)
        start_line = scan_idx
        scan_idx -= 1

        status, result = _classify_signature(signature_parts, start_line, line_idx)
        if status == 'found':
            return ('found', result)
        if status == 'invalid':
            return ('invalid', None)

    return ('incomplete', None)


def _find_function_opening(lines: list[str], line_idx: int, head: str) -> tuple[str, int] | None:
    """
    Determine whether the opening brace at line_idx belongs to a function
    definition, scanning backwards across the (possibly multi-line) signature.
    The text before the brace on the same line seeds the scan; previous lines
    are accumulated until the parameter list balances. Returns the function
    name and the signature start line, or None when the brace does not open a
    function body (control structure, namespace, class, scope block, ...).
    """
    signature_parts: list[str] = []
    start_line: int | None = None

    stripped_head = head.strip()
    if stripped_head:
        signature_parts.append(strip_trailing_qualifiers(stripped_head))
        start_line = line_idx
        status, result = _classify_signature(signature_parts, start_line, line_idx)
        if status == 'found':
            return result
        if status == 'invalid':
            return None

    status, result = _scan_previous_lines(lines, line_idx, signature_parts, start_line)
    if status == 'found':
        return result
    return None
