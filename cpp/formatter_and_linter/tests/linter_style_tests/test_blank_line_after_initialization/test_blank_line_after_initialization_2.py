#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.style_checks import check_blank_line_after_initialization


def check_code(code: str):
    return check_blank_line_after_initialization('\n'.join(code))


class TestBlankLineAfterInitialization(unittest.TestCase):
    def test_const_declarations(self):
        code = [
            'void process(double input)',
            '{',
            '    const int threshold = 10;',
            '    const double factor = input * 2.0;',
            '    processValue(threshold, factor);',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][2], 4)

    def test_multiline_signature_with_violation(self):
        code = [
            'FlightController::Result run(',
            '    FlightController& ctrl,',
            '    Aircraft& aircraft)',
            '{',
            '    ControlCommand cmd;',
            '    cmd.wing_rpm = 100;',
            '    return Result::Success;',
            '}',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 'run')

    def test_multiline_signature_with_blank_line(self):
        code = [
            'FlightController::Result run(',
            '    FlightController& ctrl,',
            '    Aircraft& aircraft)',
            '{',
            '    ControlCommand cmd;',
            '',
            '    cmd.wing_rpm = 100;',
            '',
            '    return Result::Success;',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_assignment_to_existing_var_is_not_declaration(self):
        code = [
            'void process()',
            '{',
            '    state_.mode = Mode::Auto;',
            '    cmd.wing_rpm = 100;',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_function_call_first_line_is_not_decl(self):
        code = [
            'void process()',
            '{',
            '    init();',
            '    int a = 1;',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_brace_on_same_line_with_body(self):
        code = [
            'void process() {',
            '    int a = 1;',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_empty_function_body(self):
        code = [
            'void process()',
            '{',
            '}',
        ]
        self.assertEqual(check_code(code), [])

    def test_declarations_at_end_of_function(self):
        code = [
            'void process()',
            '{',
            '    init();',
            '    int a = 1;',
            '    int b = 2;',
            '}',
        ]
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
