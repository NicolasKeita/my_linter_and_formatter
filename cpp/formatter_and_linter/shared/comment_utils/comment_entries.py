#!/usr/bin/env python3
"""
Comment flavour classification, line by line.

Each comment range returned by the scanner is turned into one entry per covered
line: ``singleline`` (own line), ``inline`` (after code), and for block comments
``multiline_start`` / ``multiline_content`` / ``multiline_end``. The placement
rule groups those entries into blocks.
"""

LINE_COMMENT = "//"

SINGLE_LINE = "singleline"
INLINE = "inline"
MULTILINE_START = "multiline_start"
MULTILINE_CONTENT = "multiline_content"
MULTILINE_END = "multiline_end"


def classify_line_comment(code: str, start: int, line_num: int) -> tuple[int, str]:
    """Distinguish a ``//`` comment on its own line from a trailing one."""
    line_start = code.rfind("\n", 0, start) + 1
    if code[line_start:start].strip():
        return line_num, INLINE
    return line_num, SINGLE_LINE


def _block_comment_entries(code: str, start: int, end: int, line_number_of) -> list[tuple[int, str]]:
    start_line = line_number_of(start)
    end_line = line_number_of(end)
    entries = [(start_line, MULTILINE_START)]
    entries.extend((num, MULTILINE_CONTENT) for num in range(start_line + 1, end_line))
    if end_line != start_line:
        entries.append((end_line, MULTILINE_END))
    return entries


def collect_comment_entries(
    code: str,
    comment_ranges: list[tuple[int, int]],
    line_number_of,
) -> list[tuple[int, str]]:
    """Return one ``(line_number, flavour)`` entry per commented line."""
    entries: list[tuple[int, str]] = []
    for start, end in comment_ranges:
        if code[start : start + 2] == LINE_COMMENT:
            entries.append(classify_line_comment(code, start, line_number_of(start)))
            continue
        entries.extend(_block_comment_entries(code, start, end, line_number_of))
    return entries
