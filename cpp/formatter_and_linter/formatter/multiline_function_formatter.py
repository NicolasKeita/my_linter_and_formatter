#!/usr/bin/env python3
"""
Multi-line Function Parameter Formatter

Re-formats C++ function definitions whose parameters are already spread over
several lines.
"""

import re

from formatter.parameter_formatter import (
    calculate_alignment,
    calculate_indentation,
    format_parameters_list,
)
from formatter.parameter_parser import extract_parameters

SIGNATURE_PATTERN = (
    r"^(\s*)((?:(?:static|inline|virtual|explicit|constexpr|const)\s+)*[\w:]+(?:\s*[*&])*)\s+([\w:]+)\s*\("
)


def _short_name(qualified_name: str) -> str:
    """Return the function name without any '::' scope prefix."""
    return qualified_name.split("::")[-1]


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
        signature_suffix = all_params[closing_index + 1 :]
        all_params = all_params[:closing_index]
    inline_body = ""
    if "{" in signature_suffix:
        suffix_part, inline_body = signature_suffix.split("{", 1)
    else:
        suffix_part = signature_suffix
    signature_suffix = suffix_part.strip().rstrip(";").strip()
    return all_params, signature_suffix, inline_body


def _render_multiline_signature(
    leading_indent: str,
    full_prefix: str,
    full_func_name: str,
    formatted_params: str,
    signature_suffix: str,
    has_brace: bool,
    inline_body: str,
) -> list[str]:
    const_part = f" {signature_suffix}" if signature_suffix else ""
    if has_brace:
        emitted = [
            f"{leading_indent}{full_prefix} {full_func_name}" f"{formatted_params}{const_part}",
            f"{leading_indent}{{",
        ]
        if inline_body:
            emitted.append(inline_body.strip())
        return emitted
    return [f"{leading_indent}{full_prefix} {full_func_name}{formatted_params};"]


def _advance_after_signature(has_brace: bool, brace_on_next_line: bool, end: int) -> int:
    if has_brace and brace_on_next_line:
        return end + 1
    return end


def format_multiline_function_params(code: str) -> str:
    """
    Format multi-line function parameters in C++ code for better readability.
    This handles cases where function parameters are already on multiple lines.

    Args:
        code: The C++ code as a string

    Returns:
        The formatted code
    """
    lines = code.splitlines()
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        match = re.match(SIGNATURE_PATTERN, line)

        if match:
            leading_indent = match.group(1)
            full_prefix = match.group(2)
            full_func_name = match.group(3)
            paren_depth = stripped.count("(") - stripped.count(")")

            if paren_depth > 0:
                param_lines, j, paren_depth = _collect_balanced_lines(lines, i, paren_depth)
                last_param_line = param_lines[-1].strip()
                is_prototype, next_line_is_brace = _resolve_prototype_flag(last_param_line, lines, j)

                if paren_depth == 0:
                    first_line_params = line[match.end() :]
                    all_params = _join_param_lines(first_line_params, param_lines)
                    has_brace = "{" in last_param_line
                    if not has_brace and next_line_is_brace:
                        has_brace = True
                    brace_on_next_line = has_brace and "{" not in last_param_line and next_line_is_brace
                    all_params, signature_suffix, inline_body = _split_signature_suffix(all_params)
                    parsed_params = extract_parameters(all_params)

                    if parsed_params and len(parsed_params) > 1:
                        max_type_len, _ = calculate_alignment(parsed_params)
                        indent = calculate_indentation(full_prefix, full_func_name, max_type_len, leading_indent)
                        formatted_params = format_parameters_list(parsed_params, indent, max_type_len)
                        result_lines.extend(
                            _render_multiline_signature(
                                leading_indent,
                                full_prefix,
                                full_func_name,
                                formatted_params,
                                signature_suffix,
                                has_brace,
                                inline_body,
                            )
                        )
                        i = _advance_after_signature(has_brace, brace_on_next_line, j)
                        continue

            result_lines.append(line)
        else:
            result_lines.append(line)

        i += 1

    return "\n".join(result_lines)
