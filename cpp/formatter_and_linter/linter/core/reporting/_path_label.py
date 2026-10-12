#!/usr/bin/env python3
"""Shared path-label helper for linter reporting."""


def get_path_label(file_path: str) -> str:
    if file_path:
        return file_path
    return "<stdin>"
