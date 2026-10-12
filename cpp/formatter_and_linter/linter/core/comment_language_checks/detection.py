#!/usr/bin/env python3
"""Comment text cleaning and language detection logic."""

from linter.core.comment_language_checks.config import (
    CONFIDENCE_MARGIN,
    MIN_SIGNIFICANT_WORDS,
    SHORT_TEXT_MARGIN,
    SHORT_TEXT_MAX_WORDS,
    get_detector,
)


def _is_natural_language_word(token: str) -> bool:
    from linter.core.comment_language_checks.config import (
        _ACRONYM_PATTERN,
        _CAMEL_CASE_WORD_PATTERN,
        _DIGIT_PATTERN,
    )
    return (
        not _DIGIT_PATTERN.search(token)
        and not _ACRONYM_PATTERN.match(token)
        and not _CAMEL_CASE_WORD_PATTERN.search(token)
    )


def clean_comment_text(comment_text: str) -> str:
    from linter.core.comment_language_checks.config import (
        _COMMENT_SYNTAX_PATTERN,
        _DOC_KEYWORD_PATTERN,
        _NON_WORD_PATTERN,
        _SEPARATOR_CHARS_PATTERN,
        _WHITESPACE_PATTERN,
    )
    text = _COMMENT_SYNTAX_PATTERN.sub(' ', comment_text)
    text = _DOC_KEYWORD_PATTERN.sub(' ', text)
    text = _SEPARATOR_CHARS_PATTERN.sub(' ', text)
    text = _NON_WORD_PATTERN.sub(' ', text)
    tokens = [token for token in text.split() if _is_natural_language_word(token)]
    return _WHITESPACE_PATTERN.sub(' ', ' '.join(tokens)).strip()


def count_significant_words(cleaned_text: str) -> int:
    return sum(
        1
        for word in cleaned_text.split()
        if sum(1 for char in word if char.isalpha()) >= 2
    )


def _compute_confidences(cleaned_text: str):
    detector = get_detector()
    return detector.compute_language_confidence_values(cleaned_text)


def _evaluate_confidence(cleaned_text: str, word_count: int) -> tuple[bool, str]:
    from lingua import Language

    confidences = _compute_confidences(cleaned_text)
    if not confidences:
        return True, ""
    if word_count <= SHORT_TEXT_MAX_WORDS:
        margin = SHORT_TEXT_MARGIN
    else:
        margin = CONFIDENCE_MARGIN
    top_language = confidences[0].language
    top_score = confidences[0].value
    english_score = next(
        (entry.value for entry in confidences if entry.language == Language.ENGLISH),
        0.0,
    )
    is_valid = (
        top_language == Language.ENGLISH
        or (top_score - english_score) < margin
    )
    return is_valid, top_language.name.title()


def evaluate_comment(comment_text: str) -> tuple[bool, str, int]:
    cleaned_text = clean_comment_text(comment_text)
    word_count = count_significant_words(cleaned_text)
    if word_count < MIN_SIGNIFICANT_WORDS:
        return True, "", word_count
    is_valid, top_language_name = _evaluate_confidence(cleaned_text, word_count)
    return is_valid, top_language_name, word_count
