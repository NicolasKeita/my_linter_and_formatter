#!/usr/bin/env python3
"""
Stripping of the trailing qualifiers of a function signature.

'const', 'noexcept', 'override', 'final' and the ref-qualifiers '&' / '&&' may
follow the closing parenthesis of a signature across several lines; removing
them makes the parenthesis detectable.
"""

TRAILING_KEYWORD_QUALIFIERS = ("const", "noexcept", "override", "final")


def _strip_keyword_qualifier(stripped: str, qualifier: str) -> str | None:
    if not stripped.endswith(qualifier):
        return None
    candidate = stripped[: -len(qualifier)]
    if candidate and not candidate[-1].isspace():
        return None
    return candidate.rstrip()


def _strip_ref_qualifier(stripped: str, suffix: str) -> str | None:
    if not stripped.endswith(suffix):
        return None
    candidate = stripped[: -len(suffix)]
    if candidate and not candidate[-1].isspace():
        return None
    return candidate.rstrip()


def strip_trailing_qualifiers(line: str) -> str:
    """Return ``line`` without its trailing cv/ref qualifiers and specifiers."""
    stripped = line.rstrip()
    changed = True

    while changed:
        changed = False
        for keyword in TRAILING_KEYWORD_QUALIFIERS:
            without_keyword = _strip_keyword_qualifier(stripped, keyword)
            if without_keyword is not None:
                stripped = without_keyword
                changed = True
                break
        if changed:
            continue
        for suffix in ("&&", "&"):
            without_ref = _strip_ref_qualifier(stripped, suffix)
            if without_ref is not None:
                stripped = without_ref
                changed = True

    return stripped
