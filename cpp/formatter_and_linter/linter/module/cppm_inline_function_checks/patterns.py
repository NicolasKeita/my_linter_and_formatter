#!/usr/bin/env python3
"""Regex patterns and keyword sets for cppm inline function detection."""

import re

_NAMESPACE_KEYWORD_PATTERN = re.compile(r'\bnamespace\b')
_TYPE_KEYWORD_PATTERN = re.compile(r'\b(?:struct|class|union|enum)\b')
_TYPE_DECLARATION_PATTERN = re.compile(r'\b(?:struct|class|union|enum)\s+\w+\s*$')
_ACCESS_LABEL_PATTERN = re.compile(r'\s*(?:public|private|protected)\s*:')
_LEADING_WHITESPACE_PATTERN = re.compile(r'\s*')
_FUNCTION_NAME_PATTERN = re.compile(r'(?:operator\s*[^\s(]*|(?:\w+::)*~?\w+)\s*$')
_WHITESPACE_RUN_PATTERN = re.compile(r'\s+')

_CONTROL_KEYWORDS = frozenset({
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'catch', 'try',
    'return', 'throw', 'delete', 'new', 'sizeof', 'alignof', 'alignas',
    'typeid', 'decltype', 'noexcept', 'static_assert', 'requires', 'using',
    'typedef', 'static_cast', 'dynamic_cast', 'reinterpret_cast',
    'const_cast', 'concept', 'co_await', 'co_yield', 'co_return',
})
