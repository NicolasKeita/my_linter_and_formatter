#!/usr/bin/env python3
"""
Comment placement rule for the C++ linter.

A comment must either sit directly above a function / declaration line or be a
file header (the first three lines, before any declaration). Everything else is
reported as misplaced. Comments are grouped into contiguous blocks so a whole
misplaced block is reported at once.
"""


def _is_contiguous_single_line(block: list[tuple[int, str]], line_num: int) -> bool:
    return bool(block) and block[-1][1] == "singleline" and block[-1][0] == line_num - 1


def _group_comment_blocks(
    comments: list[tuple[int, str]],
) -> list[list[tuple[int, str]]]:
    blocks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for line_num, comment_type in sorted(comments):
        if comment_type == "singleline":
            if _is_contiguous_single_line(current, line_num):
                current.append((line_num, comment_type))
                continue
            if current:
                blocks.append(current)
            current = [(line_num, comment_type)]
        elif comment_type == "multiline_start":
            if current:
                blocks.append(current)
            current = [(line_num, comment_type)]
        elif comment_type in ("multiline_content", "multiline_end"):
            current.append((line_num, comment_type))
        else:
            if current:
                blocks.append(current)
                current = []
            blocks.append([(line_num, comment_type)])
    if current:
        blocks.append(current)
    return blocks


def _is_header_comment(first_line: int, last_line: int, anchor_lines: set[int]) -> bool:
    if first_line > 3:
        return False
    return not anchor_lines or min(anchor_lines) > last_line


def _collect_block_violations(
    block: list[tuple[int, str]],
    anchor_lines: set[int],
) -> list[tuple[int, str]]:
    if not block:
        return []
    first_line, first_type = block[0]
    if first_type == "inline":
        return list(block)
    last_line = block[-1][0]
    if (last_line + 1) in anchor_lines:
        return []
    if _is_header_comment(first_line, last_line, anchor_lines):
        return []
    return list(block)


def check_comment_placement(
    comments: list[tuple[int, str]],
    function_lines: set[int],
    declaration_lines: set[int],
) -> list[tuple[int, str]]:
    """Return the comments that are not attached to a function / declaration."""
    anchor_lines = function_lines | declaration_lines
    invalid_comments: list[tuple[int, str]] = []
    for block in _group_comment_blocks(comments):
        invalid_comments.extend(_collect_block_violations(block, anchor_lines))
    return invalid_comments
