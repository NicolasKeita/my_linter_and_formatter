#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.designated_init_checks import (
    check_designated_init_candidates,
    format_designated_init_message,
)


def check_code(code):
    return check_designated_init_candidates('\n'.join(code))


def test_namespaced_type_declaration_is_reported():
    code = [
        'sim::control::TargetState target{};',
        'target.altitude = 10.0;',
    ]
    assert check_code(code) == [(1, 'sim::control::TargetState', 'target', ['altitude'])]


def test_nested_member_chain_is_reported():
    code = [
        'Type v{};',
        'v.sub.field = value;',
    ]
    assert check_code(code) == [(1, 'Type', 'v', ['sub.field'])]


def test_detection_inside_function_body():
    code = [
        'void run(const Context& ctx)',
        '{',
        '    SilEvent ev{};',
        '',
        '    // Initialisation du contexte',
        '    ev.timestamp = ctx.time;',
        '}',
    ]
    assert check_code(code) == [(3, 'SilEvent', 'ev', ['timestamp'])]


def test_multiple_violations_are_reported():
    code = [
        'Type first{};',
        'first.a = 1;',
        'Type second{};',
        'second.b = 2;',
    ]
    violations = check_code(code)
    assert violations == [
        (1, 'Type', 'first', ['a']),
        (3, 'Type', 'second', ['b']),
    ]


def test_pending_is_replaced_by_following_declaration():
    code = [
        'Type first{};',
        'Type second{};',
        'second.b = 2;',
    ]
    assert check_code(code) == [(2, 'Type', 'second', ['b'])]


# --- Message formatting ----------------------------------------------------
def test_message_text():
    assert format_designated_init_message('TypeVariable', 'nom_variable', ['nom_champ']) == (
        "Warning [C++20-designated-init]: Préférez l'initialisation désignée "
        "'TypeVariable nom_variable{.nom_champ = ...};' plutôt qu'une initialisation "
        "vide suivie d'une affectation."
    )


def test_multi_field_message_text():
    assert format_designated_init_message('Summary', 'summary', ['a', 'b']) == (
        "Warning [C++20-designated-init]: Préférez l'initialisation désignée "
        "'Summary summary{.a = ..., .b = ...};' plutôt qu'une initialisation "
        "vide suivie d'une affectation."
    )


def test_nested_field_message_text():
    assert format_designated_init_message('Type', 'v', ['sub.field']) == (
        "Warning [C++20-designated-init]: Préférez l'initialisation désignée "
        "'Type v{.sub.field = ...};' plutôt qu'une initialisation vide suivie d'une "
        "affectation."
    )


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
