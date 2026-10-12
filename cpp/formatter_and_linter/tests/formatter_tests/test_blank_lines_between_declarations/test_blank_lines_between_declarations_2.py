#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.declaration_blank_line_formatter import remove_blank_lines_between_declarations


def fmt(code):
    return remove_blank_lines_between_declarations('\n'.join(code))


class TestRemoveBlankLinesBetweenDeclarations(unittest.TestCase):
    def test_single_declaration_with_blank_after_unchanged(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))

    def test_reassignment_ends_zone(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    a = compute(a);',
            '    doSomething();',
            '}',
        ]
        expected = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    a = compute(a);',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_compound_assignment_not_declaration(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    state_.x += get_value();',
            '    state_.y -= 5;',
            '}',
        ]
        expected = [
            'void process()',
            '{',
            '    int a = 1;',
            '',
            '    state_.x += get_value();',
            '    state_.y -= 5;',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_stream_operator_not_declaration(self):
        code = [
            'void log()',
            '{',
            '    std::cout << "hello";',
            '',
            '    std::cout << "world";',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))

    def test_return_statement_not_declaration(self):
        code = [
            'int compute()',
            '{',
            '    int a = 1;',
            '',
            '    int b = 2;',
            '',
            '    return a + b;',
            '}',
        ]
        expected = [
            'int compute()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    return a + b;',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))


if __name__ == '__main__':
    unittest.main()
