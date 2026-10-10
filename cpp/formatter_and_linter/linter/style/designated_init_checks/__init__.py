#!/usr/bin/env python3
"""
C++20 Designated Initializer Checks

Detects variables declared with empty-brace value initialization ('Type var{};'
or 'Type var {};') whose first following executable statement (blank lines and
comments ignored) assigns one of its members ('var.champ = value;'), and
suggests a C++20 designated initializer instead of the empty initialization
followed by a member-by-member assignment.

Consecutive member assignments on the same variable ('var.a = 1; var.b = 2;')
are grouped into a single suggestion 'Type var{.a = 1, .b = 2};'.

Non-empty initializer lists ('Type var{123};', 'Type var{.a = 1};'), copies and
parenthesized initializations are never reported. Any other executable
statement interleaved between the declaration and the first member assignment
(scope brace, read of the variable, parameter passing, ...) cancels the
detection, as does a member assignment whose right-hand side reads back the
declared variable.
"""

from .patterns import DESIGNATED_INIT_MESSAGE
from .scan import check_designated_init_candidates


def format_designated_init_message(
    type_name: str,
    variable_name: str,
    field_chains: list[str],
) -> str:
    """
    Render the warning message for an empty-brace initialization followed by
    member assignments. The suggestion lists every assigned field as a C++20
    designated initializer with '...' standing for the assigned value.
    """
    designators = ', '.join(f'.{field} = ...' for field in field_chains)
    suggestion = f"{type_name.strip()} {variable_name}{{{designators}}};"
    return DESIGNATED_INIT_MESSAGE.format(suggestion=suggestion)


__all__ = ["check_designated_init_candidates", "format_designated_init_message"]
