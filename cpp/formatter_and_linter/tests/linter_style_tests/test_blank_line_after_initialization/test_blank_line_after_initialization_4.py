#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.style_checks import check_blank_line_after_initialization


def check_code(code: str):
    return check_blank_line_after_initialization('\n'.join(code))


class TestBlankLineAfterInitialization(unittest.TestCase):
    def test_comment_only_line_before_declarations(self):
        code = [
            'void process()',
            '{',
            '    // Initialize variables',
            '    int a = 1;',
            '    int b = 2;',
            '    doSomething();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 5)

    def test_string_with_semicolon_not_declared(self):
        code = [
            'void process()',
            '{',
            '    std::string msg = "hello;world";',
            '',
            '    log(msg);',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_string_with_brace_not_declared(self):
        code = [
            'void process()',
            '{',
            '    std::string msg = "hello { world";',
            '',
            '    log(msg);',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_compound_assignment_not_declaration(self):
        code = [
            'void process()',
            '{',
            '    state_.x += get_value();',
            '    state_.y -= 5;',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
