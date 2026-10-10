#!/usr/bin/env python3
"""
Line Joining

A formatting pass that merges C++ statements that were wrapped over several
lines back onto a single line whenever the merged line still fits within the
maximum line length (120 characters by default, indentation included).

See :mod:`formatter.join_lines.joining` for the entry point ``join_lines``.
"""

from .joining import join_lines

__all__ = ["join_lines"]
