#!/usr/bin/env python3
"""Message formatting for module size violations."""

MAX_IMPLEMENTATION_FILES_PER_MODULE = 8
SUB_MODULE_PLACEHOLDER = "<SubModule>"

MODULE_TOO_LARGE_MESSAGE_TEMPLATE = (
    "[WARN_MODULE_TOO_LARGE] Le module/namespace '{label}' compte {count} fichiers "
    "d'implémentation (seuil : {threshold}). Pense à le subdiviser en sous-modules "
    "(ex : '{suggestion}')."
)


def format_module_too_large_message(
    label: str,
    file_count: int,
    suggestion: str,
    max_files: int = MAX_IMPLEMENTATION_FILES_PER_MODULE,
) -> str:
    return MODULE_TOO_LARGE_MESSAGE_TEMPLATE.format(
        label=label,
        count=file_count,
        threshold=max_files,
        suggestion=suggestion,
    )
