#!/usr/bin/env python3
"""Signature-level formatting for multi-line C++ function parameters."""

import re

from formatter.params.parameter_formatter import (
    calculate_alignment,
    calculate_indentation,
    format_parameters_list,
)
from formatter.params.parameter_parser import extract_parameters
from formatter.params.signature_helpers import (
    SignatureParts,
    advance_after_signature,
    collect_balanced_lines,
    join_param_lines,
    render_multiline_signature,
    resolve_prototype_flag,
    split_signature_suffix,
)


def _try_format_signature(
    lines: list[str],
    i: int,
    match: re.Match[str],
) -> tuple[list[str], int] | None:
    """Format the multi-line signature starting at ``lines[i]``; returns the
    emitted lines plus the resume index, or None when unreformattable."""
    stripped = lines[i].strip()
    opening_depth = stripped.count("(") - stripped.count(")")
    if opening_depth <= 0:
        return None

    param_lines, j, paren_depth = collect_balanced_lines(lines, i, opening_depth)
    if paren_depth != 0:
        return None

    _, next_line_is_brace = resolve_prototype_flag(param_lines[-1].strip(), lines, j)
    first_line_params = lines[i][match.end():]
    all_params = join_param_lines(first_line_params, param_lines)
    has_brace = "{" in param_lines[-1] or next_line_is_brace
    brace_on_next_line = has_brace and "{" not in param_lines[-1] and next_line_is_brace
    all_params, signature_suffix, inline_body = split_signature_suffix(all_params)

    parsed_params = extract_parameters(all_params)
    if not parsed_params or len(parsed_params) <= 1:
        return None

    leading_indent, full_prefix, full_func_name = match.group(1), match.group(2), match.group(3)
    max_type_len, _ = calculate_alignment(parsed_params)
    indent = calculate_indentation(full_prefix, full_func_name, max_type_len, leading_indent)
    formatted_params = format_parameters_list(parsed_params, indent, max_type_len)

    parts = SignatureParts(
        leading_indent, full_prefix, full_func_name, formatted_params,
        signature_suffix, has_brace, inline_body,
    )
    return render_multiline_signature(parts), advance_after_signature(has_brace, brace_on_next_line, j)

