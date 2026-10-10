#!/usr/bin/env python3
"""Scan of empty-brace declarations followed by member assignments."""

from linter.style.style_checks import _mask_strings_and_comments

from .assignment_parse import _parse_member_assignment, _references_variable
from .patterns import _is_blank_or_comment, _parse_empty_brace_declaration


def _scan_assignment_group(
    lines: list[str],
    start: int,
    variable_name: str,
    in_block_comment: bool,
) -> tuple[list[str], int, bool]:
    """Collect consecutive member assignments of ``variable_name`` starting at
    ``lines[start]``, skipping blank and comment lines. Returns the gathered
    field chains, the index of the statement that ended the group and the
    updated block-comment state."""
    field_chains: list[str] = []
    scan_index = start
    while scan_index < len(lines):
        scan_masked, in_block_comment = _mask_strings_and_comments(lines[scan_index], in_block_comment)
        scan_stripped = scan_masked.strip()

        if _is_blank_or_comment(scan_stripped) or scan_stripped.startswith('#'):
            scan_index += 1
            continue

        if not field_chains and scan_stripped in ('{', '}'):
            break

        assignment = _parse_member_assignment(scan_stripped, variable_name)
        if assignment is None:
            break

        field_chain, rhs = assignment
        if _references_variable(rhs, variable_name):
            break

        field_chains.append(field_chain)
        scan_index += 1

    return field_chains, scan_index, in_block_comment


class _DesignatedInitScan:
    """Walk the lines of one file looking for empty-brace declarations whose
    first executable follow-up assigns a member of the declared variable."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.violations: list[tuple[int, str, str, list[str]]] = []
        self.in_block_comment = False
        self.line_index = 0

    def run(self) -> list[tuple[int, str, str, list[str]]]:
        """Scan every line and return the gathered violations."""
        while self.line_index < len(self.lines):
            stripped = self._mask_line(self.line_index)
            declaration = _parse_empty_brace_declaration(stripped)
            if self._skip(stripped) or declaration is None:
                self.line_index += 1
                continue
            self._collect_violation(declaration)
        return self.violations

    def _mask_line(self, index: int) -> str:
        """Mask strings and comments of ``lines[index]`` and strip the result."""
        masked, self.in_block_comment = _mask_strings_and_comments(
            self.lines[index], self.in_block_comment
        )
        return masked.strip()

    @staticmethod
    def _skip(stripped: str) -> bool:
        """Tell whether the line must be ignored (blank, comment or preprocessor)."""
        return _is_blank_or_comment(stripped) or stripped.startswith('#')

    def _collect_violation(self, declaration: tuple[str, str]) -> None:
        """Gather the member-assignment group that follows the declaration and
        record a violation when at least one field was assigned."""
        type_name, variable_name = declaration
        field_chains, scan_index, self.in_block_comment = _scan_assignment_group(
            self.lines, self.line_index + 1, variable_name, self.in_block_comment
        )
        if field_chains:
            self.violations.append((self.line_index + 1, type_name, variable_name, field_chains))
            self.line_index = scan_index
        else:
            self.line_index += 1


def check_designated_init_candidates(
    code: str,
) -> list[tuple[int, str, str, list[str]]]:
    """
    Report empty-brace declarations whose first following executable statement
    (blank lines and comments ignored) assigns a member of the declared
    variable, as (declaration_line, type, variable_name, field_chains) tuples
    with 1-based line numbers.

    Consecutive plain assignments on the same variable are gathered into a
    single violation. Any executable statement interleaved before the first
    member assignment, a right-hand side that reads back the declared variable,
    or a scope brace cancels the detection. When the gathered group is closed
    by a non-assignment statement (for example an unrelated call), the fields
    already collected are reported and the scan resumes after that statement.
    """
    return _DesignatedInitScan(code.splitlines()).run()
