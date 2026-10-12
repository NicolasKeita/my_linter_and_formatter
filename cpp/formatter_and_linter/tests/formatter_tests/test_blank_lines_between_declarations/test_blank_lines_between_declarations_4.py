#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.declaration_blank_line_formatter import remove_blank_lines_between_declarations


def fmt(code):
    return remove_blank_lines_between_declarations('\n'.join(code))


class TestRemoveBlankLinesBetweenDeclarations(unittest.TestCase):
    def test_namespace_body_not_compacted(self):
        code = [
            'namespace sim {',
            'int x = 1;',
            '',
            'int y = 2;',
            'doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))

    def test_struct_body_not_compacted(self):
        code = [
            'struct Config',
            '{',
            '    int x = 1;',
            '',
            '    int y = 2;',
            '};',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))

    def test_lambda_not_treated_as_function(self):
        code = [
            'void pass()',
            '{',
            '    auto lam = [](int v) { return v + 1; };',
            '',
            '    const int r = lam(2);',
            '',
            '    consume(r);',
            '}',
        ]
        expected = [
            'void pass()',
            '{',
            '    auto lam = [](int v) { return v + 1; };',
            '    const int r = lam(2);',
            '',
            '    consume(r);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_multiline_declaration_continuation(self):
        code = [
            'void init()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(',
            '        0.0, 1.0);',
            '',
            '    const double r = unit(generator);',
            '',
            '    apply(r);',
            '}',
        ]
        expected = [
            'void init()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(',
            '        0.0, 1.0);',
            '    const double r = unit(generator);',
            '',
            '    apply(r);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_aggregate_initialiser_spanning_lines(self):
        code = [
            'void init()',
            '{',
            '    Point p = {',
            '        1,',
            '        2,',
            '    };',
            '',
            '    const int total = p.x + p.y;',
            '',
            '    use(total);',
            '}',
        ]
        expected = [
            'void init()',
            '{',
            '    Point p = {',
            '        1,',
            '        2,',
            '    };',
            '    const int total = p.x + p.y;',
            '',
            '    use(total);',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))


if __name__ == '__main__':
    unittest.main()
