#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.function_parameter_count_checks import (
    WARN_FUNCTION_TOO_MANY_PARAMETERS_TAG,
    check_function_parameter_count,
    format_function_parameter_count_message,
)


def check_code(code):
    if isinstance(code, list):
        code = '\n'.join(code)
    return check_function_parameter_count(code)


class TestFunctionParameterCount(unittest.TestCase):
    def test_template_function_is_detected(self):
        code = [
            'template<typename Target>',
            'bool parse_option(CliOptions& opts, int argc, char* argv[], int& idx,',
            '                  Target& field, std::string_view label) {',
            '    return true;',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'parse_option')
        self.assertEqual(violations[0][2], 6)

    def test_multiple_violations_are_reported_in_line_order(self):
        code = [
            'void first(int a, int b, int c, int d, int e, int f) { return; }',
            'void second(int a, int b, int c, int d, int e, int f) { return; }',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 2)
        self.assertEqual(violations[0][0], 'first')
        self.assertEqual(violations[0][1], 1)
        self.assertEqual(violations[1][0], 'second')
        self.assertEqual(violations[1][1], 2)

    def test_declaration_is_not_flagged(self):
        code = 'void foo(int a, int b, int c, int d, int e, int f);'
        self.assertEqual(check_code(code), [])

    def test_comment_commas_are_not_counted(self):
        code = [
            '/* void old(int a, int b, int c, int d, int e, int f) { return; } */',
            'void foo() { return; }',
        ]
        self.assertEqual(check_code(code), [])

    def test_message_format_matches_specification(self):
        message = format_function_parameter_count_message(
            'Src/App/Application.cpp', 'Run', 42, 6
        )
        self.assertEqual(
            message,
            '[WARN_FUNCTION_TOO_MANY_PARAMETERS] Src/App/Application.cpp:42 : '
            "la fonction 'Run' possède 6 paramètres (max : 5). "
            'Envisagez de regrouper certains paramètres dans une structure ou classe.',
        )

    def test_warning_tag_constant(self):
        self.assertEqual(
            WARN_FUNCTION_TOO_MANY_PARAMETERS_TAG,
            '[WARN_FUNCTION_TOO_MANY_PARAMETERS]',
        )


if __name__ == '__main__':
    unittest.main()
