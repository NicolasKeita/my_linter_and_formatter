#!/usr/bin/env python3
"""Block emission of the member alignment pass."""

from shared.declaration_parse import DeclarationParts

from .scan_state import BlockItem


def _rebuild_declaration(declaration: DeclarationParts, target_column: int) -> str:
    """Rebuild one declaration line with its name starting at the target column."""
    line = (
        declaration.indent
        + declaration.type_part
        + " " * (target_column - len(declaration.type_part))
        + declaration.name
        + declaration.rest
    )
    if declaration.comment:
        line = line.rstrip() + " " + declaration.comment
    return line


def _align_declarations(
    block: list[BlockItem],
    max_line_length: int,
) -> list[str] | None:
    """Compute the aligned version of every declaration of ``block``; returns
    None when the block holds no declaration or when an aligned line would
    exceed ``max_line_length`` (the caller then keeps the original lines)."""
    declarations = [item.declaration for item in block if item.declaration is not None]
    if not declarations:
        return None
    target_column = max(len(declaration.type_part) for declaration in declarations) + 1
    aligned_lines: list[str] = []
    for declaration in declarations:
        line = _rebuild_declaration(declaration, target_column)
        if len(line.rstrip()) > max_line_length:
            return None
        aligned_lines.append(line)
    return aligned_lines


def flush_block(block: list[BlockItem], output: list[str], max_line_length: int) -> None:
    """Emit the pending block in source order, aligning the member names when
    every rebuilt line stays within max_line_length, or verbatim otherwise."""
    if not block:
        return
    aligned_lines = _align_declarations(block, max_line_length)
    if aligned_lines is None:
        output.extend(item.raw_line for item in block)
    else:
        aligned_iter = iter(aligned_lines)
        for item in block:
            output.append(next(aligned_iter) if item.declaration is not None else item.raw_line)
    block.clear()
