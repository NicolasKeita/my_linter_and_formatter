#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.function_parameter_count_checks import (
    MAX_FUNCTION_PARAMETERS,
    check_function_parameter_count,
)


def check_code(code):
    if isinstance(code, list):
        code = '\n'.join(code)
    return check_function_parameter_count(code)


class TestFunctionParameterCount(unittest.TestCase):
    def test_max_parameters_constant(self):
        self.assertEqual(MAX_FUNCTION_PARAMETERS, 5)

    def test_five_parameters_is_allowed(self):
        code = 'void foo(int a, int b, int c, int d, int e) { return; }'
        self.assertEqual(check_code(code), [])

    def test_six_parameters_is_reported(self):
        code = 'void foo(int a, int b, int c, int d, int e, int f) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        name, line, count = violations[0]
        self.assertEqual(name, 'foo')
        self.assertEqual(line, 1)
        self.assertEqual(count, 6)

    def test_empty_parameter_list_is_allowed(self):
        code = 'void foo() { return; }'
        self.assertEqual(check_code(code), [])

    def test_void_parameter_is_allowed(self):
        code = 'void foo(void) { return; }'
        self.assertEqual(check_code(code), [])

    def test_one_parameter_is_allowed(self):
        code = 'void foo(int a) { return; }'
        self.assertEqual(check_code(code), [])

    def test_function_pointer_parameter_is_counted_correctly(self):
        code = 'void foo(int a, void (*cb)(int, int), int b) { return; }'
        self.assertEqual(check_code(code), [])

    def test_function_pointer_six_params_is_reported(self):
        code = 'void foo(int a, void (*cb)(int, int), int b, int c, int d, int e) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 6)

    def test_template_parameter_is_counted_correctly(self):
        code = 'void foo(std::vector<int, Alloc> v, int a) { return; }'
        self.assertEqual(check_code(code), [])

    def test_nested_template_comma_is_not_counted(self):
        code = 'void foo(std::array<std::vector<int>, 3> a, int b) { return; }'
        self.assertEqual(check_code(code), [])

    def test_template_six_params_is_reported(self):
        code = 'void foo(std::map<int, int> a, int b, int c, int d, int e, int f) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 6)

    def test_multiline_signature_is_handled(self):
        code = [
            'void foo(',
            '    int a,',
            '    int b,',
            '    int c,',
            '    int d,',
            '    int e,',
            '    int f',
            ') {',
            '    return;',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'foo')
        self.assertEqual(violations[0][1], 1)
        self.assertEqual(violations[0][2], 6)

    def test_multiline_five_params_is_allowed(self):
        code = [
            'void foo(',
            '    int a,',
            '    int b,',
            '    int c,',
            '    int d,',
            '    int e',
            ') {',
            '    return;',
            '}',
        ]
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
