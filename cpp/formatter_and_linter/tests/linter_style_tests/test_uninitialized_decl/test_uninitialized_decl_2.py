#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.uninitialized_decl_checks import (
    check_uninitialized_declarations,
)


def check_code(code):
    return check_uninitialized_declarations('\n'.join(code))


class TestUninitializedDeclarations(unittest.TestCase):
    def test_parenthesized_initialization_is_not_reported(self):
        code = [
            'TypeVar ma_var(3);',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_struct_member_declarations_are_not_reported(self):
        code = [
            'struct Config {',
            '    std::uint32_t count;',
            '',
            '    // Ratio comment',
            '    std::float64_t ratio;',
            '};',
        ]
        self.assertEqual(check_code(code), [])

    def test_function_signature_is_not_reported(self):
        code = [
            'void process(double input);',
            'process(1.0);',
        ]
        self.assertEqual(check_code(code), [])

    def test_member_function_after_member_declaration_is_not_reported(self):
        code = [
            'struct Sensor {',
            '    Calib calib;',
            '',
            '    void reset()',
            '    {',
            '        calib.scale = 1.0f;',
            '    }',
            '};',
        ]
        self.assertEqual(check_code(code), [])

    def test_detection_inside_function_body(self):
        code = [
            'void run(const Context& ctx)',
            '{',
            '    SilEvent injected;',
            '',
            '    // Initialisation du contexte',
            '    injected.timestamp = ctx.time;',
            '    injected.source = "ENV";',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 3)
        self.assertEqual(violations[0][1], 'injected')

    def test_closing_scope_cancels_detection(self):
        code = [
            'void f()',
            '{',
            '    if (cond)',
            '    {',
            '        Type ma_var;',
            '    }',
            '    ma_var.champ1 = val1;',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_keyword_statement_cancels_detection(self):
        code = [
            'TypeVar ma_var;',
            'return;',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_multiple_violations_are_reported(self):
        code = [
            'Type first;',
            'first.a = 1;',
            'Type second;',
            'second.b = 2;',
        ]
        self.assertEqual(check_code(code), [(1, 'first'), (3, 'second')])

    def test_pending_is_replaced_by_following_declaration(self):
        code = [
            'Type first;',
            'Type second;',
            'second.b = 2;',
        ]
        self.assertEqual(check_code(code), [(2, 'second')])


if __name__ == '__main__':
    unittest.main()
