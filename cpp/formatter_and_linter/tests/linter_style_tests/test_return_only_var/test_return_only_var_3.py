#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.return_only_var_checks import (
    check_return_only_variable,
)


def check_code(code):
    return check_return_only_variable('\n'.join(code))


def test_call_between_declaration_and_return_is_not_reported():
    code = [
        'auto x = compute();',
        'log(x);',
        'return x;',
    ]
    assert check_code(code) == []


def test_direct_return_expression_is_not_reported():
    code = [
        'return SensorValidity{ .altitude_valid = true };',
    ]
    assert check_code(code) == []


def test_uninitialized_declaration_is_not_reported():
    code = [
        'Type x;',
        'return x;',
    ]
    assert check_code(code) == []


def test_multiple_declarators_are_not_reported():
    code = [
        'auto a = 1, b = 2;',
        'return a;',
    ]
    assert check_code(code) == []


def test_two_statements_on_one_line_are_not_reported():
    code = [
        'auto x = 1; prepare();',
        'return x;',
    ]
    assert check_code(code) == []


def test_string_content_is_ignored():
    code = [
        'auto x = 1;',
        'log("return x;");',
        'return x;',
    ]
    assert check_code(code) == []


def test_closing_scope_cancels_detection():
    code = [
        'void f()',
        '{',
        '    if (cond)',
        '    {',
        '        auto x = 1;',
        '    }',
        '    return x;',
        '}',
    ]
    assert check_code(code) == []


# --- Multiple violations & chaining --------------------------------------
def test_multiple_violations_are_reported():
    code = [
        'auto a = 1;',
        'return a;',
        'auto b = 2;',
        'return b;',
    ]
    assert check_code(code) == [(1, 'a'), (3, 'b')]


def test_new_declaration_replaces_pending_one():
    code = [
        'auto a = 1;',
        'auto b = 2;',
        'return b;',
    ]
    assert check_code(code) == [(2, 'b')]


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
