#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.style_checks import check_blank_line_after_initialization


def check_code(code: str):
    return check_blank_line_after_initialization('\n'.join(code))


class TestBlankLineAfterInitialization(unittest.TestCase):
    def test_missing_blank_line_is_reported(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'process')
        self.assertEqual(violations[0][2], 4)

    def test_present_blank_line_is_not_reported(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_single_declaration_without_blank_line(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 3)

    def test_no_declarations_no_violation(self):
        code = [
            'void process()',
            '{',
            '    doSomething();',
            '    doSomethingElse();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_declarations_then_return_without_blank(self):
        code = [
            'int compute()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '    return a + b;',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'compute')
        self.assertEqual(violations[0][2], 4)

    def test_declarations_then_return_with_blank(self):
        code = [
            'int compute()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    return a + b;',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_mixed_declarations_and_assignments(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    a = compute(a);',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 3)


if __name__ == '__main__':
    unittest.main()
