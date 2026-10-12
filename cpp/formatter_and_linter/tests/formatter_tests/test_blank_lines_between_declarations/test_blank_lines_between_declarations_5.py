#!/usr/bin/env python3
"""Tests split into part 5."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.declaration_blank_line_formatter import remove_blank_lines_between_declarations


def fmt(code):
    return remove_blank_lines_between_declarations('\n'.join(code))


class TestRemoveBlankLinesBetweenDeclarations(unittest.TestCase):
    def test_whitespace_only_blank_lines_count_as_blank(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '   ',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        expected = [
            'void process()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_trailing_newline_preserved(self):
        code = 'void f()\n{\n    int a = 1;\n\n    int b = 2;\n\n    use(a, b);\n}\n'
        expected = 'void f()\n{\n    int a = 1;\n    int b = 2;\n\n    use(a, b);\n}\n'
        self.assertEqual(remove_blank_lines_between_declarations(code), expected)

    def test_idempotent(self):
        code = [
            'void generate_faults() {',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '',
            '    std::uniform_real_distribution<std::float64_t> window(2.0, 12.0);',
            '',
            '    const std::uint64_t roll = generator() % 6;',
            '',
            '    apply(roll);',
            '}',
        ]
        once = fmt(code)
        self.assertEqual(fmt(once.splitlines()), once)

    def test_empty_input(self):
        self.assertEqual(remove_blank_lines_between_declarations(''), '')

    def test_leading_blank_after_brace_preserved(self):
        code = [
            'void process()',
            '{',
            '',
            '    int a = 1;',
            '',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        expected = [
            'void process()',
            '{',
            '',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))


if __name__ == '__main__':
    unittest.main()
