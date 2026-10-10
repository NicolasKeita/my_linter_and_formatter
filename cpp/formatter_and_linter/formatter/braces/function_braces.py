#!/usr/bin/env python3
"""Function Brace Formatter: put function opening braces on their own line."""

from shared.brace_utils import (
    extract_function_name,
    find_brace_positions,
    is_constructor_initializer_continuation,
    is_initializer_list,
    is_lambda_capture,
)
from shared.function_analysis import find_function_start_for_brace


def _declaration_indent(before_brace: str, lines: list[str], line_idx: int) -> int:
    """Indent of the declaration carrying the brace, resolved through the
    signature line when the brace continues a constructor initializer list."""
    func_decl = before_brace.rstrip()
    base_indent = len(func_decl) - len(func_decl.lstrip())
    if is_constructor_initializer_continuation(before_brace):
        func_start_idx = find_function_start_for_brace(lines, line_idx + 1)
        if func_start_idx is not None:
            func_start_line = lines[func_start_idx]
            base_indent = len(func_start_line) - len(func_start_line.lstrip())
    return base_indent


def _emit_inline_body(brace_indent: str, after_brace: str, result_lines: list[str]) -> None:
    """Emit the body that followed the brace on the same line, under the brace."""
    if not after_brace.strip():
        return
    content = after_brace.strip()
    if content.endswith('}'):
        body_content = content[:-1].rstrip().rstrip(';')
        if body_content:
            result_lines.append(brace_indent + '    ' + body_content + ';')
        result_lines.append(brace_indent + '}')
    else:
        result_lines.append(brace_indent + '    ' + content)


def _split_function_brace(
    line: str,
    pos: int,
    lines: list[str],
    line_idx: int,
    result_lines: list[str],
) -> bool:
    """Split a same-line function brace; returns True when it was split."""
    before_brace = line[:pos]
    if extract_function_name(before_brace) is None:
        return False

    after_brace = line[pos + 1:]
    func_decl = before_brace.rstrip()
    brace_indent = ' ' * _declaration_indent(before_brace, lines, line_idx)

    result_lines.append(func_decl)
    result_lines.append(brace_indent + '{')
    _emit_inline_body(brace_indent, after_brace, result_lines)
    return True


def _align_lone_brace(line: str, result_lines: list[str]) -> bool:
    """Align a lone '{' line with the function signature above it; returns
    True when the aligned brace was appended."""
    if line.strip() != '{':
        return False
    func_start_idx = find_function_start_for_brace(result_lines, len(result_lines))
    if func_start_idx is None:
        return False
    func_line = result_lines[func_start_idx] if func_start_idx < len(result_lines) else ""
    base_indent = len(func_line) - len(func_line.lstrip())
    result_lines.append(' ' * base_indent + '{')
    return True


def _process_brace_line(
    line: str,
    line_idx: int,
    lines: list[str],
    result_lines: list[str],
) -> bool:
    """Process every brace of ``line``; True when the line was fully handled."""
    for pos, brace_type in find_brace_positions(line):
        if brace_type != '{':
            continue

        if is_lambda_capture(line, pos) or is_initializer_list(line, pos):
            result_lines.append(line)
            return True

        before_brace = line[:pos]
        local_paren_depth = before_brace.count('(') - before_brace.count(')')
        if local_paren_depth == 0 and '(' in before_brace:
            if _split_function_brace(line, pos, lines, line_idx, result_lines):
                return True
    return False


def format_function_braces(code: str) -> str:
    lines = code.splitlines()
    result_lines: list[str] = []

    for line_idx, line in enumerate(lines):
        if not find_brace_positions(line):
            result_lines.append(line)
            continue

        processed = _process_brace_line(line, line_idx, lines, result_lines)

        if not processed:
            processed = _align_lone_brace(line, result_lines)

        if not processed:
            result_lines.append(line)

    return '\n'.join(result_lines) + ('\n' if code.endswith('\n') else '')

