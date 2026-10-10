#!/usr/bin/env python3
"""
Member Variable Alignment Formatter

Vertical alignment pass for C++20 module interface files. Inside every
struct / class body, contiguous runs of member variable declarations get
their variable names aligned on a single column. The target column is
computed from the longest declaration type of the contiguous block plus one
separator space, so the initializer ('=' or '{') that follows the name stays
attached to the name instead of being pushed to its own column.

A block is broken (and the alignment recomputed) by blank lines, methods,
macros / preprocessor directives, visibility changes ('public:', 'private:',
'protected:'), closing braces or any other non-variable statement. Pure
comment lines are neutral: they neither join nor break a block. Trailing
line comments are detached before reformatting and re-attached after the
final semicolon of the rebuilt line, separated by a single space.

Complex types are supported: namespaced names ('a::b::C'), templates
('<...>', nested and containing commas or integer literals), fixed-width
types ('std::uint64_t'), qualifiers ('const', 'static', 'constexpr',
'mutable', 'unsigned', ...), pointers and references, array suffixes
('[3]', '[N][M]') and leading attributes ('[[no_unique_address]]').
Declarations that cannot be parsed with certainty (bit-fields, function
pointers, multiple declarators, elaborated type specifiers, ...) are left
untouched and simply break the surrounding block.

The pass only processes module interface files: every other extension
(.cpp, .hpp, .h, ...) is returned untouched.
"""

from .alignment_pass import AlignmentPass

CPPM_EXTENSION = ".cppm"

MAX_LINE_LENGTH = 120


def align_member_variables(code: str, max_line_length: int = MAX_LINE_LENGTH) -> str:
    """Align member variable names inside every struct / class body of the code."""
    if not code:
        return code
    output = AlignmentPass(max_line_length).run(code.splitlines())
    aligned = "\n".join(output)
    if code.endswith("\n"):
        aligned += "\n"
    return aligned


def format_member_alignment_for_file(
    file_path: str,
    code: str,
    max_line_length: int = MAX_LINE_LENGTH,
) -> str:
    """Apply the alignment pass only when file_path is a .cppm module interface.

    Every other extension (.cpp, .hpp, .h, ...) is returned untouched: the
    rule is exclusive to C++20 module interface files.
    """
    if not file_path.lower().endswith(CPPM_EXTENSION):
        return code
    return align_member_variables(code, max_line_length)


__all__ = ["align_member_variables", "format_member_alignment_for_file"]
