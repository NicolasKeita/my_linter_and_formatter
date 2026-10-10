#!/usr/bin/env python3
"""Scan of initialized declarations immediately followed by 'return var;'."""

from linter.style.style_checks import _mask_strings_and_comments

from .declaration_scan import _find_declaration_end
from .patterns import (
    _RETURN_VAR_RE,
    _is_blank_or_comment,
    _is_single_complete_declaration,
    _parse_initialized_declaration,
    _top_level_semicolon_index,
)


class _ReturnOnlyVarScan:
    """Walk the lines of one file tracking the declaration pending its return."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.violations: list[tuple[int, str]] = []
        self.in_block_comment = False
        self.line_index = 0
        self.pending_name: str | None = None
        self.pending_line = 0

    def run(self) -> list[tuple[int, str]]:
        """Scan every line and return the gathered violations."""
        while self.line_index < len(self.lines):
            stripped = self._mask_line()
            if self._skip(stripped):
                self.line_index += 1
                continue
            if self.pending_name is not None:
                self._advance_pending(stripped)
            else:
                self._start_pending(stripped)
        return self.violations

    def _mask_line(self) -> str:
        """Mask strings and comments of the current line and strip the result."""
        masked, self.in_block_comment = _mask_strings_and_comments(
            self.lines[self.line_index], self.in_block_comment
        )
        return masked.strip()

    @staticmethod
    def _skip(stripped: str) -> bool:
        """Tell whether the line must be ignored (blank, comment or preprocessor)."""
        return _is_blank_or_comment(stripped) or stripped.startswith('#')

    def _advance_pending(self, stripped: str) -> None:
        """Resolve the pending declaration: record a violation on a matching
        'return var;', start a new pending declaration or drop the pending one."""
        return_match = _RETURN_VAR_RE.match(stripped)
        if return_match is not None and return_match.group('name') == self.pending_name:
            self.violations.append((self.pending_line, self.pending_name))
            self.pending_name = None
            self.line_index += 1
            return

        self.pending_name = None
        declared_name = _parse_initialized_declaration(stripped)
        if declared_name is not None and _is_single_complete_declaration(stripped):
            self.pending_name = declared_name
            self.pending_line = self.line_index + 1
        self.line_index += 1

    def _start_pending(self, stripped: str) -> None:
        """Open a pending declaration on the current line, consuming its
        continuation lines when the declaration spans several lines."""
        declared_name = _parse_initialized_declaration(stripped)
        if declared_name is None:
            self.line_index += 1
            return

        decl_start = self.line_index
        if _is_single_complete_declaration(stripped):
            self.pending_name = declared_name
            self.pending_line = decl_start + 1
            self.line_index += 1
            return

        if self._declaration_ends(stripped):
            self.line_index += 1
            return

        end_index, self.in_block_comment = _find_declaration_end(
            self.lines, decl_start, self.in_block_comment
        )
        if end_index is None:
            self.line_index += 1
            return

        self.pending_name = declared_name
        self.pending_line = decl_start + 1
        self.line_index = end_index + 1

    def _declaration_ends(self, stripped: str) -> bool:
        """Tell whether the declaration statement terminates on this line."""
        return _top_level_semicolon_index(stripped) is not None


def check_return_only_variable(code: str) -> list[tuple[int, str]]:
    """
    Report local variables declared/initialized and then immediately returned
    via 'return var;' as their first following executable statement (blank
    lines and comments ignored), as (declaration_line, variable_name) tuples
    with 1-based line numbers.

    Any interleaved executable instruction, a return of a modified expression
    (member access, function call, arithmetic, ...) or a return of a different
    identifier cancels the detection. A pending declaration that is not
    followed by a matching return is discarded as soon as another executable
    statement appears.
    """
    return _ReturnOnlyVarScan(code.splitlines()).run()
