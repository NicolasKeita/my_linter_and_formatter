#!/usr/bin/env python3
"""Scan of sanitised code for functions with too many parameters."""

from linter.module.cppm_inline_function_checks import (
    _Block,
    _BlockKind,
    _classify_header,
    _compute_line_starts,
    _is_braced_initializer,
    _line_of_position,
    _split_header,
)

from .parameter_count import _count_parameters


class _ParameterScan:
    """Walk sanitised code, classifying every top-level brace as a block
    opening and recording functions whose parameter count is too high."""

    def __init__(self, sanitized: str, max_params: int) -> None:
        self.sanitized = sanitized
        self.max_params = max_params
        self.line_starts = _compute_line_starts(sanitized)
        self.blocks: list[_Block] = []
        self.violations: list[tuple[str, int, int]] = []
        self.segment_start = 0
        self.paren_depth = 0

    def run(self) -> list[tuple[str, int, int]]:
        """Scan the whole code and return violations sorted by line number."""
        index = 0
        length = len(self.sanitized)
        while index < length:
            char = self.sanitized[index]
            if char == '(':
                self.paren_depth += 1
            elif char == ')':
                self.paren_depth = max(0, self.paren_depth - 1)
            elif char == '{' and self.paren_depth == 0:
                self._open_block(index)
            elif char == '}' and self.paren_depth == 0:
                self._close_block(index)
            elif char == ';' and self.paren_depth == 0:
                self.segment_start = index + 1
            index += 1
        self.violations.sort(key=lambda violation: violation[1])
        return self.violations

    def _record_function(self, significant_header: str, header_start: int, name: str) -> None:
        """Append a violation when the function declares too many parameters."""
        param_count = _count_parameters(significant_header)
        if param_count > self.max_params:
            start_line = _line_of_position(self.line_starts, header_start) + 1
            self.violations.append((name, start_line, param_count))

    def _open_block(self, index: int) -> None:
        """Classify the '{' at ``index`` as a braced initializer or as the
        opening brace of a classified block."""
        if _is_braced_initializer(self.sanitized, self.segment_start, index):
            self.blocks.append(_Block(_BlockKind.OTHER, '', index, index, True))
            return
        header = self.sanitized[self.segment_start:index]
        significant_header, offset = _split_header(header)
        kind, name = _classify_header(significant_header)
        header_start = self.segment_start + offset
        self.blocks.append(_Block(kind, name, index, header_start, False))
        self.segment_start = index + 1
        if kind == _BlockKind.FUNCTION:
            self._record_function(significant_header, header_start, name)

    def _close_block(self, index: int) -> None:
        """Pop the innermost block; a non-transparent block restarts the
        current segment after its closing brace."""
        if self.blocks:
            block = self.blocks.pop()
            if not block.transparent:
                self.segment_start = index + 1
        else:
            self.segment_start = index + 1


def _scan_for_parameter_count(
    sanitized: str,
    max_params: int,
) -> list[tuple[str, int, int]]:
    """
    Scan sanitised code for function definitions whose parameter count
    exceeds max_params. Returns a list of (name, start_line, param_count)
    tuples sorted by line number.
    """
    return _ParameterScan(sanitized, max_params).run()
