#!/usr/bin/env python3
"""Multi-line declaration continuation helpers for the return-only variable check."""

from linter.style.style_checks import _mask_strings_and_comments

from .patterns import (
    _is_blank_or_comment,
    _is_single_complete_declaration,
    _top_level_semicolon_index,
)


def _declaration_ends_on_line(stripped_masked: str) -> bool:
    """
    Whether a declaration statement terminates on this masked line.

    A declaration ends at the first top-level ';' that is outside parentheses
    and outside the braced/parenthesized initializer. When the initializer is
    a copy initialization ('name = expr;'), the terminating ';' is top-level.
    """
    return _top_level_semicolon_index(stripped_masked) is not None


def _declaration_continues_on_line(stripped_masked: str) -> bool:
    """
    Whether a masked, stripped line is a plausible continuation of an
    in-progress multi-line declaration (part of its initializer).

    A line that terminates the declaration (top-level ';') is handled
    separately by _declaration_ends_on_line. A standalone scope brace at
    top level (e.g. a closing '}' that is not part of the initializer) is not
    a continuation and cancels the pending declaration.
    """
    if stripped_masked in ('{', '}'):
        return False
    return True


def _find_declaration_end(
    lines: list[str],
    start_index: int,
    in_block_comment: bool,
) -> tuple[int | None, bool]:
    """
    Starting at start_index (a line that begins an initialized declaration),
    scan forward until the declaration terminates (top-level ';' outside the
    initializer). Return (end_index, in_block_comment) where end_index is the
    0-based index of the terminating line, or (None, in_block_comment) when the
    declaration never terminates before another complete declaration, a
    non-continuation statement, a scope closed or end of file.
    """
    index = start_index
    block_comment = in_block_comment

    while index < len(lines):
        masked, block_comment = _mask_strings_and_comments(lines[index], block_comment)
        stripped = masked.strip()

        if _is_blank_or_comment(stripped) or stripped.startswith('#'):
            index += 1
            continue

        if _is_single_complete_declaration(stripped):
            return index, block_comment

        if _declaration_ends_on_line(stripped):
            return None, block_comment

        if not _declaration_continues_on_line(stripped):
            return None, block_comment

        index += 1

    return None, block_comment
