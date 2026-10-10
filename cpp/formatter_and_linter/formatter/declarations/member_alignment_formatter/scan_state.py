#!/usr/bin/env python3
"""Scope tracking for the member alignment pass."""

import re
from typing import NamedTuple

from shared.declaration_parse import DeclarationParts

CLASS_HEADER_REGEX = re.compile(
    r"^\s*(?:export\s+)?(?:template\s*<[^<>]*>\s*)?(?:struct|class|union)\b"
)

PREPROCESSOR_REGEX = re.compile(r"^\s*#")


class BlockItem(NamedTuple):
    """One buffered block entry: a parsed declaration or a neutral line
    (comment) kept in source order until the block is emitted."""

    declaration: DeclarationParts | None
    raw_line: str


class ScanState:
    """Brace-depth tracker that knows which scopes are struct/class bodies.

    'depth' counts the braces currently open. 'class_stack' stores, for each
    open struct / class / union body, the depth value measured right after
    its opening brace: a line is a member declaration candidate when it is
    processed while 'depth' equals that stored value. 'pending_header_depth'
    remembers a class header seen on a previous line whose opening brace has
    not been consumed yet (Allman brace style).
    """

    def __init__(self) -> None:
        self.depth = 0
        self.class_stack: list[int] = []
        self.pending_header_depth: int | None = None
        self.in_block_comment = False

    def in_class_body(self) -> bool:
        return bool(self.class_stack) and self.depth == self.class_stack[-1]

    def update(self, masked_code: str) -> None:
        """Consume one code line (literals masked) and update the scope state."""
        has_header = CLASS_HEADER_REGEX.match(masked_code) is not None
        if has_header:
            self.pending_header_depth = self.depth
        header_consumed = self._consume_braces(masked_code, has_header)
        if self.pending_header_depth is not None and not header_consumed:
            if (
                "{" in masked_code
                or "}" in masked_code
                or masked_code.rstrip().endswith(";")
            ):
                self.pending_header_depth = None

    def _consume_braces(self, masked_code: str, has_header: bool) -> bool:
        """Walk the braces of ``masked_code`` updating the scope stack; tells
        whether the pending class header's opening brace was consumed here."""
        header_consumed = False
        for char in masked_code:
            if char == "{":
                can_open_class = (
                    self.pending_header_depth is not None
                    and not header_consumed
                    and self.depth == self.pending_header_depth
                    and (has_header or masked_code.strip() == "{")
                )
                self.depth += 1
                if can_open_class:
                    self.class_stack.append(self.depth)
                    self.pending_header_depth = None
                    header_consumed = True
            elif char == "}":
                self.depth = max(0, self.depth - 1)
                while self.class_stack and self.depth < self.class_stack[-1]:
                    self.class_stack.pop()
                self.pending_header_depth = None
        return header_consumed
