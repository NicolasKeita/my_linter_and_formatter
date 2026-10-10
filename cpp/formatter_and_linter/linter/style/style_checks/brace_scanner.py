#!/usr/bin/env python3
"""Shared brace/parenthesis scanner used by the style rules."""

from .scanning import _mask_strings_and_comments


class BraceScanner:
    """Track top-level '{' / '}' across masked C++ lines.

    ``iter_braces`` yields ``(line_index, char_index, head, is_open)`` for every
    top-level brace, where ``head`` is the masked text before the brace on that
    line (empty for a closing brace). Preprocessor lines are skipped.
    """

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self.paren_depth = 0
        self.scope_depth = 0
        self.in_block_comment = False

    def iter_braces(self):
        for line_index, raw_line in enumerate(self._lines):
            masked_line, self.in_block_comment = _mask_strings_and_comments(
                raw_line, self.in_block_comment
            )
            if masked_line.strip().startswith('#'):
                continue
            for char_index, char in enumerate(masked_line):
                if char == '(':
                    self.paren_depth += 1
                elif char == ')':
                    if self.paren_depth > 0:
                        self.paren_depth -= 1
                elif char == '{' and self.paren_depth == 0:
                    yield line_index, char_index, masked_line[:char_index], True
                elif char == '}' and self.paren_depth == 0:
                    yield line_index, char_index, '', False

