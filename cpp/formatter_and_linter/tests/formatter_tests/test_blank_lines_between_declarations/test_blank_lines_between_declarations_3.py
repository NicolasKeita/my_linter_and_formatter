#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.declaration_blank_line_formatter import remove_blank_lines_between_declarations


def fmt(code):
    return remove_blank_lines_between_declarations('\n'.join(code))


class TestRemoveBlankLinesBetweenDeclarations(unittest.TestCase):
    def test_designated_initialiser_declaration(self):
        code = [
            'void build()',
            '{',
            '    ControlCommand cmd{.throttle = 1, .pitch = 2};',
            '',
            '    ControlCommand other{.throttle = 0};',
            '',
            '    dispatch(cmd);',
            '}',
        ]
        expected = [
            'void build()',
            '{',
            '    ControlCommand cmd{.throttle = 1, .pitch = 2};',
            '    ControlCommand other{.throttle = 0};',
            '',
            '    dispatch(cmd);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_template_with_constructor_call(self):
        code = [
            'void sample()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '',
            '    std::uniform_real_distribution<std::float64_t> window(2.0, 12.0);',
            '',
            '    const double r = unit(generator);',
            '',
            '    apply(r);',
            '}',
        ]
        expected = [
            'void sample()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '    std::uniform_real_distribution<std::float64_t> window(2.0, 12.0);',
            '    const double r = unit(generator);',
            '',
            '    apply(r);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_control_structure_blank_lines_preserved(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    if (a > 0) {',
            '',
            '        use(b);',
            '    }',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))

    def test_multiple_functions_in_file(self):
        code = [
            'void first()',
            '{',
            '    int a = 1;',
            '',
            '    int b = 2;',
            '',
            '    run(a, b);',
            '}',
            '',
            'void second()',
            '{',
            '    int c = 3;',
            '    doMore(c);',
            '}',
        ]
        expected = [
            'void first()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    run(a, b);',
            '}',
            '',
            'void second()',
            '{',
            '    int c = 3;',
            '    doMore(c);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))


if __name__ == '__main__':
    unittest.main()
