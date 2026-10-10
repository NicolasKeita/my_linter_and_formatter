#!/usr/bin/env python3
"""
Designated Initializer Split Formatter

A formatting pass that splits single-line C++ declarations using a braced
initializer with C++20 designated initializers ('.field = value') over
several lines whenever the line exceeds the maximum line length (120
characters by default, indentation included).

The declaration and its opening brace stay on the original line, every
designated field is moved to its own line and the closing '};' is placed on
its own line. The field indentation is the column of the variable name plus
a constant offset (4 spaces) and the closing brace is aligned with the
variable name column, so the vertical alignment of the types and variable
names of the surrounding declarations (the 'table' alignment) is preserved.

Only top-level commas are used as split points: commas nested inside
function calls, template argument lists ('<...>') or nested braced
sub-initializers never break a sub-expression. A trailing comma is always
added after the last field and an optional trailing line comment is kept on
the closing brace line.

Lines that already fit within the maximum length, statements without a
designated initializer (plain braced lists, enumerators, class / struct /
namespace bodies, lambdas, call arguments) and statements that are already
split are left untouched, which makes the pass idempotent.
"""

from .segment_split import FIELD_INDENT, _split_statement_line

MAX_LINE_LENGTH = 120


def split_long_designated_initializations(code: str, max_length: int = MAX_LINE_LENGTH) -> str:
    """
    Split declarations using a designated initializer that exceed max_length
    over several lines, one field per line.
    """
    if not code:
        return code
    lines = code.split("\n")
    result: list[str] = []
    for line in lines:
        if len(line.rstrip()) > max_length:
            result.extend(_split_statement_line(line))
        else:
            result.append(line)
    return "\n".join(result)


__all__ = ["split_long_designated_initializations", "MAX_LINE_LENGTH", "FIELD_INDENT"]
