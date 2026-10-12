#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.designated_init_checks import (
    check_designated_init_candidates,
)


def check_code(code):
    return check_designated_init_candidates('\n'.join(code))


# --- Required cases -------------------------------------------------------
def test_empty_braces_then_member_assignment_is_reported():
    code = [
        'TypeVariable nom_variable{};',
        'nom_variable.nom_champ = valeur;',
    ]
    violations = check_code(code)
    assert violations == [(1, 'TypeVariable', 'nom_variable', ['nom_champ'])]


def test_empty_braces_with_space_then_member_assignment_is_reported():
    code = [
        'TypeVariable nom_variable {};',
        'nom_variable.nom_champ = valeur;',
    ]
    violations = check_code(code)
    assert violations == [(1, 'TypeVariable', 'nom_variable', ['nom_champ'])]


def test_extra_spaces_inside_braces_are_accepted():
    code = [
        'Type v { } ;',
        'v.champ = 1;',
    ]
    assert check_code(code) == [(1, 'Type', 'v', ['champ'])]


# --- Multi-field grouping -------------------------------------------------
def test_consecutive_member_assignments_are_grouped():
    code = [
        'Summary summary{};',
        'summary.a = 1;',
        'summary.b = 2;',
    ]
    violations = check_code(code)
    assert violations == [(1, 'Summary', 'summary', ['a', 'b'])]


def test_interleaved_statement_stops_grouping_but_reports_first_field():
    code = [
        'Summary summary{};',
        'summary.a = 1;',
        'do_something_else();',
        'summary.b = 2;',
    ]
    assert check_code(code) == [(1, 'Summary', 'summary', ['a'])]


def test_assignment_to_other_variable_stops_grouping():
    code = [
        'Summary summary{};',
        'summary.a = 1;',
        'other.b = 2;',
        'summary.c = 3;',
    ]
    assert check_code(code) == [(1, 'Summary', 'summary', ['a'])]


# --- Blank lines / comments are ignored ------------------------------------
def test_blank_lines_and_comments_are_ignored():
    code = [
        'SilEvent ev{};',
        '',
        '// Initialisation du contexte',
        'ev.timestamp = ctx.time;',
    ]
    assert check_code(code) == [(1, 'SilEvent', 'ev', ['timestamp'])]


def test_block_comment_is_ignored():
    code = [
        'SilEvent ev{};',
        '/* Initialization',
        '   spans lines */',
        'ev.timestamp = ctx.time;',
    ]
    assert check_code(code) == [(1, 'SilEvent', 'ev', ['timestamp'])]


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
