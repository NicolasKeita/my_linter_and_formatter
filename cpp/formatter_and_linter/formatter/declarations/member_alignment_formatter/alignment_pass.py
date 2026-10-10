#!/usr/bin/env python3
"""Per-line walk of the member alignment pass."""

from shared.declaration_parse import mask_literals, parse_declaration, split_trailing_comment

from .block_flush import flush_block
from .scan_state import PREPROCESSOR_REGEX, BlockItem, ScanState


class AlignmentPass:
    """Walk one file line by line, buffering member declarations of struct /
    class bodies and flushing aligned blocks on every interruption."""

    def __init__(self, max_line_length: int) -> None:
        self.state = ScanState()
        self.output: list[str] = []
        self.block: list[BlockItem] = []
        self.max_line_length = max_line_length

    def run(self, lines: list[str]) -> list[str]:
        """Process every line and return the aligned output."""
        for line in lines:
            self.process_line(line)
        flush_block(self.block, self.output, self.max_line_length)
        return self.output

    def _buffer_comment(self, line: str, stripped_code: str) -> None:
        """Keep a comment-only (or block-comment continuation) line in the block."""
        if stripped_code:
            self.state.update(mask_literals(stripped_code))
        self.block.append(BlockItem(declaration=None, raw_line=line))

    def _parse_member(self, code_part: str, comment_part: str, line: str):
        """Parse ``line`` as a member declaration when inside a class body."""
        if not (self.state.in_class_body() and code_part.rstrip().endswith(";")):
            return None
        return parse_declaration(code_part, comment_part, line)

    def process_line(self, line: str) -> None:
        """Handle one source line: buffer comments and member declarations,
        flush the pending block on blank lines, preprocessor directives and
        any non-declaration statement."""
        was_in_block_comment = self.state.in_block_comment
        code_part, comment_part, block_comment_state = split_trailing_comment(
            line, self.state.in_block_comment
        )
        self.state.in_block_comment = block_comment_state
        stripped_code = code_part.strip()

        if was_in_block_comment or (not stripped_code and (comment_part or block_comment_state)):
            self._buffer_comment(line, stripped_code)
            return

        if not stripped_code or PREPROCESSOR_REGEX.match(stripped_code):
            flush_block(self.block, self.output, self.max_line_length)
            self.output.append(line)
            return

        parsed = self._parse_member(code_part, comment_part, line)
        if parsed is None:
            flush_block(self.block, self.output, self.max_line_length)
            self.output.append(line)
        else:
            self.block.append(BlockItem(declaration=parsed, raw_line=line))
        self.state.update(mask_literals(stripped_code))
