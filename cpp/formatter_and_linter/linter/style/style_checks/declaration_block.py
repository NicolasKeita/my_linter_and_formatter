#!/usr/bin/env python3
"""Blank-line-after-initialization rule and its body-scanning helpers."""

from .brace_scanner import BraceScanner
from .declaration_classify import _is_declaration_line
from .scanning import _mask_strings_and_comments


def _skip_leading_blank_lines(lines: list[str], body_idx: int, in_block_comment: bool) -> tuple[int, bool]:
    """Advance past blank lines after the opening brace; return (index, comment_state)."""
    while body_idx < len(lines):
        masked, in_block_comment = _mask_strings_and_comments(lines[body_idx], in_block_comment)
        if masked.strip() == '':
            body_idx += 1
            continue
        break
    return body_idx, in_block_comment


def _advance_to_statement_end(lines: list[str], group_end: int, in_block_comment: bool) -> tuple[int, bool, bool]:
    """Advance group_end until the current declaration ends with ';' or '}'.

    Returns (index, comment_state, reached_end).
    """
    block_masked, in_block_comment = _mask_strings_and_comments(lines[group_end], in_block_comment)
    block_stripped = block_masked.strip()
    while not (block_stripped.endswith(';') or block_stripped.endswith('}')):
        group_end += 1
        if group_end >= len(lines):
            return group_end, in_block_comment, True
        block_masked, in_block_comment = _mask_strings_and_comments(lines[group_end], in_block_comment)
        block_stripped = block_masked.strip()
    return group_end, in_block_comment, False


def _scan_declaration_group(lines: list[str], body_idx: int, in_block_comment: bool) -> int | None:
    """Scan the leading declaration group; return index just past it or None."""
    group_end = body_idx
    while group_end < len(lines):
        block_masked, in_block_comment = _mask_strings_and_comments(lines[group_end], in_block_comment)
        block_stripped = block_masked.strip()
        if not block_stripped:
            break
        if not _is_declaration_line(block_stripped):
            break
        group_end, in_block_comment, reached_end = _advance_to_statement_end(
            lines, group_end, in_block_comment
        )
        if reached_end:
            return None
        group_end += 1
    return group_end


def _scan_body_for_declaration_block(
    lines: list[str],
    brace_line_index: int,
    in_block_comment: bool,
) -> int | None:
    """
    Scan the function body starting after the opening brace at brace_line_index.
    Return the 0-based line index of the last declaration in the first block
    when a blank line is missing after it, or None when the rule is satisfied
    or no declaration block is present.
    """
    body_idx, in_block_comment = _skip_leading_blank_lines(
        lines, brace_line_index + 1, in_block_comment
    )

    if body_idx >= len(lines):
        return None

    first_masked, in_block_comment = _mask_strings_and_comments(lines[body_idx], in_block_comment)
    if not _is_declaration_line(first_masked.strip()):
        return None

    group_end = _scan_declaration_group(lines, body_idx, in_block_comment)
    if group_end is None or group_end >= len(lines):
        return None

    if lines[group_end].strip() == '':
        return None

    return group_end - 1


def check_blank_line_after_initialization(code: str) -> list[tuple[str, int, int]]:
    """
    Detect functions where the first block of local variable declarations is not
    separated from the following statements by a blank line.

    Returns a list of (function_name, function_start_line, last_declaration_line)
    tuples (1-based line numbers).
    """
    from .function_length import _find_function_opening

    lines = code.splitlines()
    violations: list[tuple[str, int, int]] = []
    scanner = BraceScanner(lines)

    for line_index, _, head, is_open in scanner.iter_braces():
        if not is_open:
            continue
        scanner.scope_depth += 1
        if head.strip() != '':
            continue
        opening = _find_function_opening(lines, line_index, head)
        if opening is None:
            continue
        func_name, start_line = opening
        last_decl = _scan_body_for_declaration_block(lines, line_index, scanner.in_block_comment)
        if last_decl is not None:
            violations.append((func_name, start_line + 1, last_decl + 1))

    return violations
