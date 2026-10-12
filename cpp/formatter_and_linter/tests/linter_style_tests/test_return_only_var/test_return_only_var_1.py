#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.return_only_var_checks import (
    check_return_only_variable,
)


def check_code(code):
    return check_return_only_variable('\n'.join(code))


# --- Required cases -------------------------------------------------------
def test_single_line_declaration_then_return_is_reported():
    code = [
        'auto x = 1;',
        'return x;',
    ]
    violations = check_code(code)
    assert violations == [(1, 'x')]


def test_multiline_designated_initializers_with_comments_is_reported():
    code = [
        'const SensorValidity validity{',
        '    .altitude_valid = !std::isnan(telemetry.z),',
        '    .position_valid = horizontal <= limits.max_position_m',
        '};',
        '',
        '// Returns the computed validity',
        'return validity;',
    ]
    violations = check_code(code)
    assert violations == [(1, 'validity')]


def test_executable_code_between_declaration_and_return_is_not_reported():
    code = [
        'const auto status = evaluate();',
        'log_status(status);',
        'return status;',
    ]
    assert check_code(code) == []


# --- Additional detection coverage ---------------------------------------
def test_parenthesized_constructor_initialization_is_reported():
    code = [
        'auto result = compute_something(a, b);',
        'return result;',
    ]
    assert check_code(code) == [(1, 'result')]


def test_direct_constructor_call_initialization_is_reported():
    code = [
        'const Widget w(get_widget());',
        'return w;',
    ]
    assert check_code(code) == [(1, 'w')]


def test_const_qualified_declaration_is_reported():
    code = [
        'const auto value = compute();',
        'return value;',
    ]
    assert check_code(code) == [(1, 'value')]


def test_declaration_line_number_is_reported_not_return_line():
    code = [
        'void f()',
        '{',
        '    auto x = 1;',
        '    return x;',
        '}',
    ]
    assert check_code(code) == [(3, 'x')]


def test_multiline_parenthesized_initializer_is_reported():
    code = [
        'auto result = compute(',
        '    a,',
        '    b',
        ');',
        'return result;',
    ]
    assert check_code(code) == [(1, 'result')]


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
