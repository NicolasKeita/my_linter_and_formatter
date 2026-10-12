#!/usr/bin/env python3
"""Comment Language Check package: public API re-exported for callers."""

from linter.core.comment_language_checks.config import (
    CONFIDENCE_MARGIN,
    LINGUA_AVAILABLE,
    MIN_SIGNIFICANT_WORDS,
    SHORT_TEXT_MARGIN,
    SHORT_TEXT_MAX_WORDS,
)
from linter.core.comment_language_checks.detection import evaluate_comment
from linter.core.comment_language_checks.extraction import extract_comment_texts


def check_comment_language(comment_text: str) -> bool:
    if not LINGUA_AVAILABLE:
        return True
    is_valid, _, _ = evaluate_comment(comment_text)
    return is_valid


def check_code_comments_language(code: str) -> list[tuple[int, str]]:
    if not LINGUA_AVAILABLE:
        return []
    violations = []
    for line_num, comment_text in extract_comment_texts(code):
        is_valid, top_language_name, word_count = evaluate_comment(comment_text)
        if word_count < MIN_SIGNIFICANT_WORDS:
            continue
        if not is_valid:
            violations.append((line_num, top_language_name))
    return violations


__all__ = [
    "LINGUA_AVAILABLE",
    "MIN_SIGNIFICANT_WORDS",
    "CONFIDENCE_MARGIN",
    "SHORT_TEXT_MAX_WORDS",
    "SHORT_TEXT_MARGIN",
    "extract_comment_texts",
    "check_comment_language",
    "check_code_comments_language",
]
