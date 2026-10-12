#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.function_parameter_count_checks import (
    check_function_parameter_count,
)


def check_code(code):
    if isinstance(code, list):
        code = '\n'.join(code)
    return check_function_parameter_count(code)


class TestFunctionParameterCount(unittest.TestCase):
    def test_constructor_with_initializer_list(self):
        code = [
            'Foo::Foo(int a, int b, int c, int d, int e, int f) : x_(a), y_(b) {',
            '    init();',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'Foo::Foo')
        self.assertEqual(violations[0][2], 6)

    def test_member_function_with_const_qualifier(self):
        code = 'void Foo::bar(int a, int b, int c, int d, int e, int f) const { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'Foo::bar')
        self.assertEqual(violations[0][2], 6)

    def test_member_function_five_params_is_allowed(self):
        code = 'void Foo::bar(int a, int b, int c, int d, int e) const { return; }'
        self.assertEqual(check_code(code), [])

    def test_function_inside_class_is_detected(self):
        code = [
            'class Foo {',
            'public:',
            '    void bar(int a, int b, int c, int d, int e, int f) { return; }',
            '};',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'bar')
        self.assertEqual(violations[0][1], 3)
        self.assertEqual(violations[0][2], 6)

    def test_default_parameters_are_counted(self):
        code = 'void foo(int a = 1, int b = 2, int c = 3, int d = 4, int e = 5, int f = 6) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 6)

    def test_variadic_is_counted_as_parameter(self):
        code = 'void foo(int a, int b, int c, int d, int e, ...) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 6)

    def test_lambda_is_not_flagged(self):
        code = 'auto f = [](int a, int b, int c, int d, int e, int f) { return a; };'
        self.assertEqual(check_code(code), [])

    def test_function_call_is_not_flagged(self):
        code = [
            'void run() {',
            '    compute(a, b, c, d, e, f);',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_control_structures_are_not_flagged(self):
        code = [
            'int main() {',
            '    if (a > 0) { return 1; }',
            '    for (int i = 0; i < 10; ++i) { step(); }',
            '    while (x > 0) { --x; }',
            '    return 0;',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_braced_default_value_commas_are_not_counted(self):
        code = 'void foo(int a = {1, 2, 3}, int b, int c, int d, int e) { return; }'
        self.assertEqual(check_code(code), [])

    def test_braced_default_six_params_is_reported(self):
        code = 'void foo(int a = {1, 2}, int b, int c, int d, int e, int f) { return; }'
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 6)

    def test_array_parameter_brackets_are_handled(self):
        code = 'void foo(int a[], int b, int c, int d, int e) { return; }'
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
