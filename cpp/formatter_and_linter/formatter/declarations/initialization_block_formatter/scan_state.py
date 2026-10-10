#!/usr/bin/env python3
"""Scan helpers and mutable state of the initialization-block formatter."""


class FormatterState:
    """Mutable state walked over the lines of one file.

    ``result`` accumulates the emitted lines, ``comment_buffer`` holds comment
    lines that are only flushed once the next code line is classified, and the
    remaining flags track whether the scan currently sits inside a function
    body and inside its leading initialization block.
    """

    def __init__(self) -> None:
        self.result: list[str] = []
        self.in_function = False
        self.brace_depth = 0
        self.in_init_block = False
        self.has_declarations = False
        self.comment_buffer: list[str] = []

    def flush_comments(self) -> None:
        if self.comment_buffer:
            self.result.extend(self.comment_buffer)
            self.comment_buffer = []


def collect_block_comment(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect a '/* ... */' comment starting at start, returning lines and next index."""
    collected = [lines[start]]
    i = start
    if "*/" not in lines[start].strip():
        i += 1
        while i < len(lines):
            collected.append(lines[i])
            if "*/" in lines[i]:
                break
            i += 1
    return collected, i + 1


def append_statement_tail(
    lines: list[str],
    start: int,
    brace_depth: int,
    result: list[str],
) -> tuple[int, int]:
    """Append continuation lines of a declaration statement, tracking brace depth."""
    i = start
    while i < len(lines) and not (lines[i].strip().endswith(";") or lines[i].strip().endswith("}")):
        i += 1
        if i < len(lines):
            brace_depth += lines[i].count("{")
            brace_depth -= lines[i].count("}")
            result.append(lines[i])
    return i + 1, brace_depth
