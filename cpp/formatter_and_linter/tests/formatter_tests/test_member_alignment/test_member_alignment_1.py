#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.member_alignment_formatter import (
    align_member_variables,
)


def align_lines(lines, **kwargs):
    return align_member_variables("\n".join(lines) + "\n", **kwargs).splitlines()


def member_line(indent, type_part, name, rest, target):
    return indent + type_part + " " * (target - len(type_part)) + name + rest


class TestMemberAlignment(unittest.TestCase):
    def test_spec_example_block_is_aligned(self):
        code = [
            "struct SilConfig {",
            "    double dt = 0.01;",
            "    sim::control::TargetState target{.z = 10.0};",
            "    sim::control::ControllerConfig controller{.hover_rpm = Aircraft{}.hover_rpm()};",
            "    SensorValidationLimits sensor_limits{};",
            "};",
        ]
        target = len("sim::control::ControllerConfig") + 1
        expected = [
            code[0],
            member_line("    ", "double", "dt", " = 0.01;", target),
            member_line("    ", "sim::control::TargetState", "target", "{.z = 10.0};", target),
            member_line(
                "    ",
                "sim::control::ControllerConfig",
                "controller",
                "{.hover_rpm = Aircraft{}.hover_rpm()};",
                target,
            ),
            member_line("    ", "SensorValidationLimits", "sensor_limits", "{};", target),
            code[5],
        ]
        self.assertEqual(align_lines(code), expected)

    def test_complex_types_are_padded_from_longest_type(self):
        code = [
            "struct Payload {",
            "    const std::uint64_t id = 0;",
            "    std::array<std::uint8_t, 4> checksum{};",
            "    unsigned long counter = 0;",
            "    const AircraftState* state_ptr = nullptr;",
            "};",
        ]
        target = len("std::array<std::uint8_t, 4>") + 1
        expected = [
            code[0],
            member_line("    ", "const std::uint64_t", "id", " = 0;", target),
            member_line("    ", "std::array<std::uint8_t, 4>", "checksum", "{};", target),
            member_line("    ", "unsigned long", "counter", " = 0;", target),
            member_line("    ", "const AircraftState*", "state_ptr", " = nullptr;", target),
            code[5],
        ]
        self.assertEqual(align_lines(code), expected)

    def test_blank_line_starts_new_block(self):
        code = [
            "struct S {",
            "    double alpha = 1.0;",
            "    int beta = 2;",
            "",
            "    long_type_name gamma = 3.0;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    double alpha = 1.0;")
        self.assertEqual(result[2], "    int    beta = 2;")
        self.assertEqual(result[4], "    long_type_name gamma = 3.0;")

    def test_visibility_specifier_resets_block(self):
        code = [
            "class C {",
            "public:",
            "    int a = 1;",
            "    long_name b = 2;",
            "private:",
            "    double c = 3.0;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[0], "class C {")
        self.assertEqual(result[1], "public:")
        self.assertEqual(result[2], "    int       a = 1;")
        self.assertEqual(result[3], "    long_name b = 2;")
        self.assertEqual(result[4], "private:")
        self.assertEqual(result[5], "    double c = 3.0;")
        self.assertEqual(result[6], "};")


if __name__ == "__main__":
    unittest.main()
