#!/usr/bin/env python3
"""Compiled patterns and token sets used by the line-joining pass."""

import re

_CONTROL_HEADER = re.compile(r"^\s*(?:if|else|for|while|switch|catch|do|try)\b")
_CONTROL_HEADER_LINE = re.compile(r"^\s*(?:if|else|for|while|switch|catch|do|try)\b(?:.*\))?\s*$")
_TYPE_HEADER = re.compile(r"^\s*(?:namespace|class|struct|union|enum)\b")
_OPEN_BRACE_HEADER = re.compile(r"(?:\)|\]|else|do|try)\s*\{$")
_ENUM_START = re.compile(r"^\s*enum\b")

_FUNC_DEF_START = re.compile(
    r"^\s*(?:(?:static|inline|virtual|explicit|constexpr|const)\s+)*"
    r"[\w:<>]+(?:\s*[*&])*\s+([\w:<>]+)\s*\("
)
_QUALIFIED_SIG_START = re.compile(r"^\s*[\w:<>,]+::~?[\w:]+\s*\(")
_ACCESS_SPECIFIER = re.compile(r"^\s*(?:public|private|protected)\s*:\s*$")
_CASE_LABEL = re.compile(r"^\s*(?:case\b.*|default)\s*:\s*\{?\s*$")
_LABEL = re.compile(r"^\s*[A-Za-z_]\w*\s*:\s*$")

_END_TOKENS = ("&&", "||", "<<", ">>", "->")
_END_SINGLE = set("=,([{+-*/:.")

_START_TOKENS = ("&&", "||", "<<", ">>", "->")
_START_SINGLE = set("=,([{+-*/:.)];")
_UNARY_START = set("+-*&!~")
