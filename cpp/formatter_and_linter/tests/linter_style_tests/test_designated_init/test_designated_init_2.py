#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.designated_init_checks import (
    check_designated_init_candidates,
)


def check_code(code):
    return check_designated_init_candidates('\n'.join(code))


def test_trailing_comment_on_declaration_is_ignored():
    code = [
        'Type v{}; // the variable under test',
        'v.champ = 1;',
    ]
    assert check_code(code) == [(1, 'Type', 'v', ['champ'])]


# --- Exclusions ------------------------------------------------------------
def test_non_empty_braced_initializer_is_not_reported():
    code = [
        'Type v{123};',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_designated_initializer_is_not_reported():
    code = [
        'Type v{.champ = 1};',
        'v.other = 2;',
    ]
    assert check_code(code) == []


def test_copy_initialization_is_not_reported():
    code = [
        'Type v = {};',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_compound_assignment_cancels_detection():
    code = [
        'Type v{};',
        'v.champ += 1;',
    ]
    assert check_code(code) == []


def test_comparison_cancels_detection():
    code = [
        'Type v{};',
        'v.champ == valeur;',
    ]
    assert check_code(code) == []


def test_rhs_reading_declared_variable_cancels_detection():
    code = [
        'Type v{};',
        'v.y = v.x + 1;',
    ]
    assert check_code(code) == []


def test_rhs_passing_declared_variable_cancels_detection():
    code = [
        'Type v{};',
        'v.y = helper(v);',
    ]
    assert check_code(code) == []


def test_interleaved_read_before_first_assignment_cancels():
    code = [
        'Type v{};',
        'use(v);',
        'v.champ = 1;',
    ]
    assert check_code(code) == []


def test_interleaved_call_before_first_assignment_cancels():
    code = [
        'Type v{};',
        'do_something();',
        'v.champ = 1;',
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
