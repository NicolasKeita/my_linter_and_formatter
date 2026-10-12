#!/usr/bin/env python3
"""Comment text extraction from C++ source code."""

from shared.comment_utils import scan_string_and_comment_ranges


def _is_in_range(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in ranges)


def _clean_multiline_text(raw_text: str) -> str:
    lines = []
    for line in raw_text.splitlines():
        cleaned = line.strip()
        cleaned = cleaned.lstrip('*').strip()
        if cleaned:
            lines.append(cleaned)
    return ' '.join(lines)


def _extract_block_comments(
    code: str,
    comment_ranges,
    string_ranges,
) -> tuple[list[tuple[int, str]], list[tuple[int, int]]]:
    comments = []
    block_comment_ranges = []
    for start, block_end in comment_ranges:
        if code[start:start + 2] != '/*':
            continue
        line_num = code[:start].count('\n') + 1
        text = _clean_multiline_text(code[start:block_end][2:-2])
        if text:
            comments.append((line_num, text))
        block_comment_ranges.append((start, block_end))
    return comments, block_comment_ranges


def _extract_line_comments(code: str, comment_ranges, string_ranges, block_comment_ranges) -> list[tuple[int, str]]:
    comments = []
    for start, _end in comment_ranges:
        if code[start:start + 2] != '//':
            continue
        if _is_in_range(start, string_ranges) or _is_in_range(start, block_comment_ranges):
            continue
        line_num = code[:start].count('\n') + 1
        end_pos = code.find('\n', start)
        if end_pos == -1:
            end_pos = len(code)
        text = code[start + 2:end_pos].strip()
        if text:
            comments.append((line_num, text))
    return comments


def extract_comment_texts(code: str) -> list[tuple[int, str]]:
    string_ranges, comment_ranges = scan_string_and_comment_ranges(code)
    block_comments, block_comment_ranges = _extract_block_comments(code, comment_ranges, string_ranges)
    line_comments = _extract_line_comments(code, comment_ranges, string_ranges, block_comment_ranges)
    return block_comments + line_comments
