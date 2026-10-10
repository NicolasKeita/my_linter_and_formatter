#!/usr/bin/env python3
"""
Advanced Function Brace Formatter

Alternative brace placement pass that also joins multi-line function
signatures onto a single line before putting the brace on its own line.
"""


from shared.brace_utils import (
    extract_function_name,
    find_brace_positions,
)

_CONTROL_KEYWORDS = ('if', 'while', 'for', 'switch', 'catch')


def _try_join_multiline_signature(lines: list[str], i: int, result_lines: list[str]) -> int | None:
    """When ``lines[i]`` starts a multi-line function signature whose body
    opens with a lone '{' on line j, join the signature lines, emit the brace
    and return the next index (j + 1); None when no signature matches."""
    stripped = lines[i].strip()
    if not ('(' in stripped and not stripped.endswith('{') and not stripped.endswith(';')):
        return None
    func_name = extract_function_name(stripped)
    if func_name is None or stripped.startswith(_CONTROL_KEYWORDS):
        return None

    paren_depth = stripped.count('(') - stripped.count(')')
    j = i + 1
    while j < len(lines) and paren_depth > 0:
        paren_depth += lines[j].strip().count('(') - lines[j].strip().count(')')
        j += 1

    if paren_depth != 0 or j >= len(lines):
        return None
    if not lines[j].strip().startswith('{'):
        return None

    func_decl = ' '.join(func_line.strip() for func_line in lines[i:j])
    result_lines.append(func_decl.rstrip())
    result_lines.append('{')
    after_brace = lines[j].strip()[1:].lstrip()
    if after_brace:
        result_lines.append(after_brace)
    return j + 1


def _split_same_line_brace(line: str, result_lines: list[str]) -> bool:
    """Split a same-line function brace: emit the declaration and the brace on
    its own line. Returns True when the brace was split."""
    for pos, brace_type in find_brace_positions(line):
        if brace_type != '{':
            continue
        before_brace = line[:pos]
        local_paren_depth = before_brace.count('(') - before_brace.count(')')
        if local_paren_depth != 0 or '(' not in before_brace:
            continue
        if extract_function_name(before_brace) is None:
            continue
        after_brace = line[pos + 1:].lstrip()
        result_lines.append(before_brace.rstrip())
        result_lines.append('{')
        if after_brace:
            result_lines.append(after_brace)
        return True
    return False


def format_function_braces_advanced(code: str) -> str:
    lines = code.splitlines()
    result_lines: list[str] = []
    i = 0

    while i < len(lines):
        next_index = _try_join_multiline_signature(lines, i, result_lines)
        if next_index is not None:
            i = next_index
            continue

        if not _split_same_line_brace(lines[i], result_lines):
            result_lines.append(lines[i])
        i += 1

    return '\n'.join(result_lines)
