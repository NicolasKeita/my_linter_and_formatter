#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.declaration_blank_line_formatter import remove_blank_lines_between_declarations


def fmt(code):
    return remove_blank_lines_between_declarations('\n'.join(code))


class TestRemoveBlankLinesBetweenDeclarations(unittest.TestCase):
    PROMPT_SAME_LINE_CODE = [
        'void generate_faults() {',
        '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
        '',
        '    std::uniform_real_distribution<std::float64_t> time_window(2.0, 12.0);',
        '',
        '    std::uniform_real_distribution<std::float64_t> duration_window(1.0, 8.0);',
        '',
        '    const std::uint64_t fault_roll = generator() % 6;',
        '',
        '    SimulationResult result{.sil_result = sil_result, .failure_reason = FailureReason::None};',
        '',
        '    const std::float64_t dx = sil_result.final_x_m - 0.0;',
        '',
        '    apply_fault(fault_roll);',
        '',
        '    if (dx > 0) {',
        '',
        '        do_something();',
        '    }',
        '}',
    ]

    def test_prompt_example_same_line_brace(self):
        expected = [
            'void generate_faults() {',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '    std::uniform_real_distribution<std::float64_t> time_window(2.0, 12.0);',
            '    std::uniform_real_distribution<std::float64_t> duration_window(1.0, 8.0);',
            '    const std::uint64_t fault_roll = generator() % 6;',
            '    SimulationResult result{.sil_result = sil_result, .failure_reason = FailureReason::None};',
            '    const std::float64_t dx = sil_result.final_x_m - 0.0;',
            '',
            '    apply_fault(fault_roll);',
            '',
            '    if (dx > 0) {',
            '',
            '        do_something();',
            '    }',
            '}',
        ]
        self.assertEqual(fmt(self.PROMPT_SAME_LINE_CODE), '\n'.join(expected))

    def test_prompt_example_own_line_brace(self):
        code = [
            'void generate_faults()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '',
            '    std::uniform_real_distribution<std::float64_t> time_window(2.0, 12.0);',
            '',
            '    const std::uint64_t fault_roll = generator() % 6;',
            '',
            '    apply_fault(fault_roll);',
            '',
            '    if (dx > 0) {',
            '',
            '        do_something();',
            '    }',
            '}',
        ]
        expected = [
            'void generate_faults()',
            '{',
            '    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);',
            '    std::uniform_real_distribution<std::float64_t> time_window(2.0, 12.0);',
            '    const std::uint64_t fault_roll = generator() % 6;',
            '',
            '    apply_fault(fault_roll);',
            '',
            '    if (dx > 0) {',
            '',
            '        do_something();',
            '    }',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(expected))

    def test_no_blank_lines_is_unchanged(self):
        code = [
            'void process()',
            '{',
            '    int a = 1;',
            '    int b = 2;',
            '',
            '    doSomething();',
            '}',
        ]
        self.assertEqual(fmt(code), '\n'.join(code))


if __name__ == '__main__':
    unittest.main()
