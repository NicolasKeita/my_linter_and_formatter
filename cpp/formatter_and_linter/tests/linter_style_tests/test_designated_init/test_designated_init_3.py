#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.designated_init_checks import (
    check_designated_init_candidates,
)


def check_code(code):
    return check_designated_init_candidates('\n'.join(code))


def test_opening_scope_brace_cancels():
    code = [
        'Type v{};',
        '{',
        '    v.champ = 1;',
        '}',
    ]
    assert check_code(code) == []


def test_closing_scope_brace_cancels():
    code = [
        'void f()',
        '{',
        '    Type v{};',
        '}',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


# --- False positive guards ------------------------------------------------
def test_multiple_declarators_are_not_reported():
    code = [
        'Type a{}, b{};',
        'a.champ = 1;',
    ]
    assert check_code(code) == []


def test_two_statements_on_one_line_are_not_reported():
    code = [
        'Type v{}; prepare();',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_return_keyword_line_is_not_a_declaration():
    code = [
        'return v{};',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_function_declaration_is_not_reported():
    code = [
        'Type v();',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_string_content_is_ignored():
    code = [
        'Type v{};',
        'log("v.champ = 1");',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


# --- Additional detection coverage ----------------------------------------
def test_template_type_declaration_is_reported():
    code = [
        'std::map<std::uint32_t, std::string> lookup{};',
        'lookup.index = 1;',
    ]
    assert check_code(code) == [(1, 'std::map<std::uint32_t, std::string>', 'lookup', ['index'])]


def test_qualified_declaration_type_is_kept_in_suggestion():
    code = [
        'static const Config* cfg{};',
        'cfg.frequency = 2.0;',
    ]
    assert check_code(code) == [(1, 'static const Config*', 'cfg', ['frequency'])]


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
