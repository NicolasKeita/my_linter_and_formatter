#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.return_only_var_checks import (
    check_return_only_variable,
)


def check_code(code):
    return check_return_only_variable('\n'.join(code))


def test_blank_lines_between_declaration_and_return_are_ignored():
    code = [
        'auto x = 1;',
        '',
        '',
        'return x;',
    ]
    assert check_code(code) == [(1, 'x')]


def test_block_comment_between_declaration_and_return_is_ignored():
    code = [
        'auto x = 1;',
        '/* explain the return',
        '   on multiple lines */',
        'return x;',
    ]
    assert check_code(code) == [(1, 'x')]


def test_single_line_comment_between_declaration_and_return_is_ignored():
    code = [
        'auto x = 1;',
        '// Renvoie le statut calculé',
        'return x;',
    ]
    assert check_code(code) == [(1, 'x')]


def test_trailing_comment_on_declaration_is_ignored():
    code = [
        'auto x = 1; // the value',
        'return x;',
    ]
    assert check_code(code) == [(1, 'x')]


# --- Cancellation cases --------------------------------------------------
def test_return_of_member_access_is_not_reported():
    code = [
        'const auto status = evaluate();',
        'return status.is_valid;',
    ]
    assert check_code(code) == []


def test_return_of_method_call_is_not_reported():
    code = [
        'const auto status = evaluate();',
        'return status.to_string();',
    ]
    assert check_code(code) == []


def test_return_of_modified_expression_is_not_reported():
    code = [
        'const auto x = compute();',
        'return x + 1;',
    ]
    assert check_code(code) == []


def test_return_of_different_identifier_is_not_reported():
    code = [
        'auto x = compute();',
        'return y;',
    ]
    assert check_code(code) == []


def test_return_without_value_is_not_reported():
    code = [
        'auto x = compute();',
        'return;',
    ]
    assert check_code(code) == []


def test_assignment_between_declaration_and_return_is_not_reported():
    code = [
        'auto x = compute();',
        'x = other;',
        'return x;',
    ]
    assert check_code(code) == []


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
