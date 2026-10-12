#!/usr/bin/env python3
"""Language-detection configuration and regex patterns for comment checks."""

import re

try:
    from lingua import Language, LanguageDetectorBuilder
    LINGUA_AVAILABLE = True
except ImportError:
    LINGUA_AVAILABLE = False

MIN_SIGNIFICANT_WORDS = 3
CONFIDENCE_MARGIN = 0.15
SHORT_TEXT_MAX_WORDS = 5
SHORT_TEXT_MARGIN = 0.35

SUPPORTED_LANGUAGES = [] if not LINGUA_AVAILABLE else [
    Language.ENGLISH,
    Language.FRENCH,
    Language.SPANISH,
    Language.GERMAN,
]

_COMMENT_SYNTAX_PATTERN = re.compile(r'/\*+|\*+/|//+|\*+')
_DOC_KEYWORD_PATTERN = re.compile(
    r'\b(?:TODO|FIXME|XXX|HACK|NOTE|NOTICE|WIP|'
    r'@brief|@details|@param|@tparam|@return|@returns|@result|'
    r'@note|@warning|@see|@file|@class|@struct|@function|@throws)\b[:]?'
)
_SEPARATOR_CHARS_PATTERN = re.compile(r'[/\\_\-]+')
_CAMEL_CASE_WORD_PATTERN = re.compile(r'[a-z][A-Z]')
_ACRONYM_PATTERN = re.compile(r'^[A-Z0-9]+$')
_DIGIT_PATTERN = re.compile(r'\d')
_NON_WORD_PATTERN = re.compile(r'[^A-Za-z0-9\s]+')
_WHITESPACE_PATTERN = re.compile(r'\s+')

_detector = None


def get_detector():
    global _detector
    if _detector is None:
        _detector = (
            LanguageDetectorBuilder
            .from_languages(*SUPPORTED_LANGUAGES)
            .build()
        )
    return _detector
