#!/usr/bin/env python3
"""Declaration regex and line classification for the init-block formatter."""

import re

DECLARATION_PATTERN = re.compile(
    r"^\s*"
    r"(?:const\s+|constexpr\s+|static\s+|volatile\s+|inline\s+)?"
    r"(?!(?:return|if|for|while|switch|else|catch|goto|throw|co_return|co_yield"
    r"|co_await|case|default|delete|new|break|continue|using|typedef)\b)"
    r"(?:struct\s+|class\s+|enum\s+)?"
    r"(?:(?:unsigned|signed|long|short)\s+)*"
    r"(?:[a-zA-Z_][a-zA-Z0-9_]*::)*[a-zA-Z_][a-zA-Z0-9_]*"
    r"(?:<[^;{}]*>)?"
    r"(?:\s*::\s*[a-zA-Z_][a-zA-Z0-9_]*(?:<[^;{}]*>)?)*"
    r"(?:\s+|\s*\*+\s*|\s*\&+\s*|\s*const\s+|\s*volatile\s*)+"
    r"(?:[a-zA-Z_][a-zA-Z0-9_]*|\[\s*[a-zA-Z_][a-zA-Z0-9_]*"
    r"(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*\s*\])"
    r"\s*(?:=|\(|{|;|,)"
)


def _is_class_or_namespace_block(lines: list[str], prev_idx: int) -> bool:
    """Tell whether the '{' opens a class, struct, enum or namespace block."""
    while prev_idx >= 0:
        prev_line = lines[prev_idx].strip()
        if prev_line:
            return bool(re.search(r"\b(class|struct|enum|namespace)\b", prev_line))
        prev_idx -= 1
    return False


def _is_declaration_line(stripped: str) -> bool:
    return bool(DECLARATION_PATTERN.match(stripped))
