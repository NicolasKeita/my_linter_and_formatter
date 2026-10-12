#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.style_checks import check_blank_line_after_initialization


def check_code(code: str):
    return check_blank_line_after_initialization('\n'.join(code))


class TestBlankLineAfterInitialization(unittest.TestCase):
    def test_declarations_then_compound_statements(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    for (int i = 0; i < a; ++i) {',
            '        process();',
            '    }',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 3)

    def test_class_body_not_checked(self):
        code = [
            'class Data',
            '{',
            '    int x = 1;',
            '    int y = 2;',
            '};',
        ]
        self.assertEqual(check_code(code), [])

    def test_namespace_body_not_checked(self):
        code = [
            'namespace sim {',
            'int x = 1;',
            'int y = 2;',
            'doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_multiple_functions(self):
        code = [
            'void good()',
            '{',
            '    int a = 1;',
            '',
            '    doSomething();',
            '}',
            '',
            'void bad()',
            '{',
            '    int b = 2;',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'bad')
        self.assertEqual(violations[0][2], 10)

    def test_stream_operator_not_declaration(self):
        code = [
            'void log()',
            '{',
            '    std::cout << "hello";',
            '    std::cout << "world";',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_brace_initialized_declarations(self):
        code = [
            'void process()',
            '{',
            '    ControlCommand cmd{1, 2, 3};',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 3)

    def test_if_block_not_checked_as_function(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    if (a > 0) {',
            '        int b = 2;',
            '        use(b);',
            '    }',
            '}',
        ]
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
