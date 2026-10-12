#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.local_variable_alignment_formatter import align_first_declaration_blocks


def align(code):
    return align_first_declaration_blocks("\n".join(code) + "\n")


def aligned_line(indent, type_part, name, rest, target):
    return indent + type_part + " " * (target - len(type_part)) + name + rest


class TestLocalVariableAlignment(unittest.TestCase):
    PROMPT_EXAMPLE_CODE = [
        "void generate_faults() {",
        "    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);",
        "    std::uniform_real_distribution<std::float64_t> time_window(2.0, 12.0);",
        "    std::uniform_real_distribution<std::float64_t> duration_window(1.0, 8.0);",
        "    const std::uint64_t fault_roll = generator() % 6;",
        "    SimulationResult result{.sil_result = sil_result, .failure_reason = FailureReason::None};",
        "    const std::float64_t dx = sil_result.final_x_m - 0.0;",
        "",
        "    apply_fault(fault_roll);",
        "}",
    ]

    def test_prompt_example_is_aligned(self):
        long_type = "std::uniform_real_distribution<std::float64_t>"
        target = len(long_type) + 1
        expected = [
            "void generate_faults() {",
            aligned_line("    ", long_type, "unit", "(0.0, 1.0);", target),
            aligned_line("    ", long_type, "time_window", "(2.0, 12.0);", target),
            aligned_line("    ", long_type, "duration_window", "(1.0, 8.0);", target),
            aligned_line("    ", "const std::uint64_t", "fault_roll", " = generator() % 6;", target),
            aligned_line(
                "    ",
                "SimulationResult",
                "result",
                "{.sil_result = sil_result, .failure_reason = FailureReason::None};",
                target,
            ),
            aligned_line("    ", "const std::float64_t", "dx", " = sil_result.final_x_m - 0.0;", target),
            "",
            "    apply_fault(fault_roll);",
            "}",
        ]
        self.assertEqual(align(self.PROMPT_EXAMPLE_CODE), "\n".join(expected) + "\n")
        result = align(self.PROMPT_EXAMPLE_CODE).splitlines()
        columns = {line.index(name) for line, name in [
            (result[1], "unit"),
            (result[4], "fault_roll"),
            (result[5], "result"),
            (result[6], "dx"),
        ]}
        self.assertEqual(len(columns), 1)

    def test_only_two_declarations_align(self):
        code = [
            "void f() {",
            "    int a = 1;",
            "    std::uint64_t counter = 0;",
            "",
            "    use(a, counter);",
            "}",
        ]
        target = len("std::uint64_t") + 1
        expected = [
            "void f() {",
            aligned_line("    ", "int", "a", " = 1;", target),
            aligned_line("    ", "std::uint64_t", "counter", " = 0;", target),
            "",
            "    use(a, counter);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_single_declaration_is_unchanged(self):
        code = [
            "void f() {",
            "    std::uint64_t counter = 0;",
            "",
            "    use(counter);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")

    def test_first_block_only_second_block_left_alone(self):
        code = [
            "void f() {",
            "    int a = 1;",
            "    long_name b = 2;",
            "",
            "    do_something();",
            "",
            "    int c = 3;",
            "    long_name d = 4;",
            "}",
        ]
        result = align(code).splitlines()
        target = len("long_name") + 1
        self.assertEqual(result[1], aligned_line("    ", "int", "a", " = 1;", target))
        self.assertEqual(result[2], aligned_line("    ", "long_name", "b", " = 2;", target))
        self.assertEqual(result[4], "    do_something();")
        self.assertEqual(result[6], "    int c = 3;")
        self.assertEqual(result[7], "    long_name d = 4;")


if __name__ == "__main__":
    unittest.main()
