#!/usr/bin/env python3
"""Signature-level formatting for multi-line C++ function parameters."""

from dataclasses import dataclass

from formatter.params.parameter_formatter import (
    calculate_alignment,
    calculate_indentation,
    format_parameters_list,
)
from formatter.params.parameter_parser import extract_parameters
class _SignatureParts:
    """Grouped fields needed to render a formatted multi-line signature."""

    leading_indent: str
    full_prefix: str
    full_func_name: str
    formatted_params: str
    signature_suffix: str
    has_brace: bool
    inline_body: str


def _collect_balanced_lines(lines: list[str], start: int, depth: int) -> tuple[list[str], int, int]:
    """Collect lines until parentheses balance, returning lines, next index and depth."""
    collected = [lines[start]]
    j = start + 1
    while j < len(lines) and depth > 0:
        depth += lines[j].strip().count("(") - lines[j].strip().count(")")
        collected.append(lines[j])
        j += 1
    return collected, j, depth


def _resolve_prototype_flag(last_param_line: str, lines: list[str], end: int) -> tuple[bool, bool]:
    """Decide whether collected params are a prototype, accounting for a brace on the next line."""
    is_prototype = last_param_line.endswith(";")
    next_line_is_brace = end < len(lines) and lines[end].strip() == "{"
    if is_prototype and next_line_is_brace:
        is_prototype = False
    return is_prototype, next_line_is_brace


def _join_param_lines(first_line_params: str, param_lines: list[str]) -> str:
    all_params = first_line_params
    for k in range(1, len(param_lines)):
        all_params += " " + param_lines[k].strip()
    return all_params


def _split_signature_suffix(all_params: str) -> tuple[str, str, str]:
    """Split 'params) suffix' into (params, suffix, inline body after '{')."""
    signature_suffix = ""
    if ")" in all_params:
        closing_index = all_params.rfind(")")
        signature_suffix = all_params[closing_index + 1:]
        all_params = all_params[:closing_index]
    inline_body = ""
    if "{" in signature_suffix:
        suffix_part, inline_body = signature_suffix.split("{", 1)
    else:
        suffix_part = signature_suffix
    signature_suffix = suffix_part.strip().rstrip(";").strip()
    return all_params, signature_suffix, inline_body


def _render_multiline_signature(parts: _SignatureParts) -> list[str]:
    const_part = f" {parts.signature_suffix}" if parts.signature_suffix else ""
    if parts.has_brace:
        emitted = [
            f"{parts.leading_indent}{parts.full_prefix} {parts.full_func_name}{parts.formatted_params}{const_part}",
            f"{parts.leading_indent}{{",
        ]
        if parts.inline_body:
            emitted.append(parts.inline_body.strip())
        return emitted
    return [f"{parts.leading_indent}{parts.full_prefix} {parts.full_func_name}{parts.formatted_params};"]


def _advance_after_signature(has_brace: bool, brace_on_next_line: bool, end: int) -> int:
    if has_brace and brace_on_next_line:
        return end + 1
    return end


def _try_format_signature(
    lines: list[str],
    i: int,
    match: re.Match[str],
) -> tuple[list[str], int] | None:
    """Format the multi-line signature starting at ``lines[i]``; returns the
    emitted lines plus the resume index, or None when unreformattable."""
    stripped = lines[i].strip()
    if stripped.count("(") - stripped.count(")") <= 0:
        return None

    param_lines, j, paren_depth = _collect_balanced_lines(lines, i, stripped.count("(") - stripped.count(")"))
    if paren_depth != 0:
        return None

    _, next_line_is_brace = _resolve_prototype_flag(param_lines[-1].strip(), lines, j)
    first_line_params = lines[i][match.end():]
    all_params = _join_param_lines(first_line_params, param_lines)
    has_brace = "{" in param_lines[-1] or next_line_is_brace
    brace_on_next_line = has_brace and "{" not in param_lines[-1] and next_line_is_brace
    all_params, signature_suffix, inline_body = _split_signature_suffix(all_params)

    parsed_params = extract_parameters(all_params)
    if not parsed_params or len(parsed_params) <= 1:
        return None

    leading_indent, full_prefix, full_func_name = match.group(1), match.group(2), match.group(3)
    max_type_len, _ = calculate_alignment(parsed_params)
    indent = calculate_indentation(full_prefix, full_func_name, max_type_len, leading_indent)
    formatted_params = format_parameters_list(parsed_params, indent, max_type_len)

    parts = _SignatureParts(
        leading_indent, full_prefix, full_func_name, formatted_params,
        signature_suffix, has_brace, inline_body,
    )
    return _render_multiline_signature(parts), _advance_after_signature(has_brace, brace_on_next_line, j)
