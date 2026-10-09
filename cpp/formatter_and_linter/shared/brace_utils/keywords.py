#!/usr/bin/env python3
"""
C++ keyword sets shared by the brace and signature helpers.

``CONTROL_KEYWORDS`` lists the keywords that look like a call ``name(...)`` but
never introduce a function, so the signature parser must reject them.
"""

CONTROL_KEYWORDS = frozenset({
    "if", "else", "for", "while", "do", "switch", "catch",
    "return", "throw", "delete", "new", "sizeof", "alignof",
    "typeid", "decltype", "noexcept", "static_assert",
})
