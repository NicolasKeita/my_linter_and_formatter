#!/usr/bin/env python3
"""Low-level helpers for building a formatted multi-line C++ signature."""

from dataclasses import dataclass


@dataclass
class SignatureParts:
    """Grouped fields needed to render a formatted multi-line signature."""

    leading_indent: str
    full_prefix: str
    full_func_name: str
    formatted_params: str
    signature_suffix: str
    has_brace: bool
    inline_body: str


def collect_balanced_lines(lines: list[str], start: int, depth: int) -> tuple[list[str], int, int]:
    """Collect lines until parentheses balance, returning lines, next index and depth."""
    collected = [lines[start]]
    j = start + 1
    while j < len(lines) and depth > 0:
        depth += lines[j].strip().count("(") - lines[j].strip().count(")")
        collected.append(lines[j])
        j += 1
    return collected, j, depth


def resolve_prototype_flag(last_param_line: str, lines: list[str], end: int) -> tuple[bool, bool]:
    """Decide whether collected params are a prototype, accounting for a brace on the next line."""
    is_prototype = last_param_line.endswith(";")
    next_line_is_brace = end < len(lines) and lines[end].strip() == "{"
    if is_prototype and next_line_is_brace:
        is_prototype = False
    return is_prototype, next_line_is_brace


def join_param_lines(first_line_params: str, param_lines: list[str]) -> str:
    """Join the parameters spread across several source lines into one string."""
    all_params = first_line_params
    for k in range(1, len(param_lines)):
        all_params += " " + param_lines[k].strip()
    return all_params


def split_signature_suffix(all_params: str) -> tuple[str, str, str]:
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


def render_multiline_signature(parts: SignatureParts) -> list[str]:
    """Render the final formatted signature lines from grouped ``parts``."""
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


def advance_after_signature(has_brace: bool, brace_on_next_line: bool, end: int) -> int:
    """Return the resume index once the signature has been emitted."""
    if has_brace and brace_on_next_line:
        return end + 1
    return end
