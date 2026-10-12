#!/usr/bin/env python3
"""
Inline Function Body Checks for .cppm Module Interfaces

Forbids multi-line function bodies inside C++20 module interface files
(.cppm): implementations longer than one effective line must live in a
separate .cpp file; only single-line getters/setters are tolerated.

The implementation is split across thematic modules: literal and comment
sanitisation, brace-state scanning, header classification, effective-line
counting and the public check entry points.
"""

from pathlib import Path

from linter.module.cppm_inline_function_checks.scanner import _scan_sanitized_code
from linter.module.cppm_inline_function_checks.sanitizer import _sanitize_code

MAX_CPPM_INLINE_FUNCTION_BODY_LINES = 1

WARN_CPPM_INLINE_FUNCTION_TAG = "[WARN_CPPM_INLINE_FUNCTION]"


def check_cppm_inline_function_bodies(
    code: str,
    max_body_lines: int = MAX_CPPM_INLINE_FUNCTION_BODY_LINES
) -> list[tuple[str, int, int]]:
    sanitized = _sanitize_code(code)
    return _scan_sanitized_code(sanitized, max_body_lines)


def format_cppm_inline_function_message(
    file_path: str,
    function_name: str,
    start_line: int,
    body_lines: int
) -> str:
    return (
        f"{WARN_CPPM_INLINE_FUNCTION_TAG} {file_path}:{start_line} : "
        f"la fonction '{function_name}' possède un corps de {body_lines} lignes "
        f"effectives dans l'interface de module "
        f"(max : {MAX_CPPM_INLINE_FUNCTION_BODY_LINES}). "
        "Déplace l'implémentation dans un fichier .cpp."
    )


def check_cppm_inline_functions(file_path: Path) -> list[str]:
    if file_path.suffix != '.cppm':
        return []
    code = file_path.read_text(encoding='utf-8')
    violations = check_cppm_inline_function_bodies(code)
    return [
        format_cppm_inline_function_message(str(file_path), function_name, start_line, body_lines)
        for function_name, start_line, body_lines in violations
    ]


__all__ = [
    "MAX_CPPM_INLINE_FUNCTION_BODY_LINES",
    "WARN_CPPM_INLINE_FUNCTION_TAG",
    "check_cppm_inline_function_bodies",
    "check_cppm_inline_functions",
    "format_cppm_inline_function_message",
]
