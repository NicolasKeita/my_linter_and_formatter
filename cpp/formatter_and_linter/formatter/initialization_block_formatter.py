#!/usr/bin/env python3
"""
Initialization Block Formatter

Enforces an empty line after the first block of local variable declarations
at the beginning of a function body.
"""

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


def _collect_block_comment(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect a '/* ... */' comment starting at start, returning lines and next index."""
    collected = [lines[start]]
    i = start
    if "*/" not in lines[start].strip():
        i += 1
        while i < len(lines):
            collected.append(lines[i])
            if "*/" in lines[i]:
                break
            i += 1
    return collected, i + 1


def _is_declaration_line(stripped: str) -> bool:
    return bool(DECLARATION_PATTERN.match(stripped))


def _append_statement_tail(
    lines: list[str],
    start: int,
    brace_depth: int,
    result: list[str],
) -> tuple[int, int]:
    """Append continuation lines of a declaration statement, tracking brace depth."""
    i = start
    while i < len(lines) and not (lines[i].strip().endswith(";") or lines[i].strip().endswith("}")):
        i += 1
        if i < len(lines):
            brace_depth += lines[i].count("{")
            brace_depth -= lines[i].count("}")
            result.append(lines[i])
    return i + 1, brace_depth


def format_initialization_blocks(code: str) -> str:
    """
    Inserts an empty line after the first block of declarations in a function body.
    """
    lines = code.splitlines()
    result = []
    
    in_function = False
    brace_depth = 0
    
    in_init_block = False
    has_declarations = False
    
    comment_buffer = []
    
    def flush_comments():
        nonlocal comment_buffer
        if comment_buffer:
            result.extend(comment_buffer)
            comment_buffer = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not in_function:
            result.append(line)
            if stripped == "{":
                prev_idx = i - 1
                is_class_or_namespace = _is_class_or_namespace_block(lines, prev_idx)
                
                if not is_class_or_namespace:
                    in_function = True
                    brace_depth = 1
                    in_init_block = True
                    has_declarations = False
            i += 1
            continue

        if stripped.startswith("//"):
            comment_buffer.append(line)
            i += 1
            continue

        if stripped.startswith("/*"):
            collected, i = _collect_block_comment(lines, i)
            comment_buffer.extend(collected)
            continue

        brace_depth += stripped.count("{")
        brace_depth -= stripped.count("}")

        if brace_depth == 0:
            flush_comments()
            in_function = False
            in_init_block = False
            result.append(line)
            i += 1
            continue

        if not in_init_block:
            flush_comments()
            result.append(line)
            i += 1
            continue

        if not stripped:
            if has_declarations:
                in_init_block = False
            flush_comments()
            result.append(line)
            i += 1
            continue

        is_decl = _is_declaration_line(stripped)

        if is_decl:
            has_declarations = True
            flush_comments()
            result.append(line)
            i, brace_depth = _append_statement_tail(lines, i, brace_depth, result)
        else:
            if has_declarations:
                result.append("")
            in_init_block = False
            flush_comments()
            result.append(line)
            i += 1

    flush_comments()
    return '\n'.join(result) + ('\n' if code.endswith('\n') else '')

__all__ = ["format_initialization_blocks"]
