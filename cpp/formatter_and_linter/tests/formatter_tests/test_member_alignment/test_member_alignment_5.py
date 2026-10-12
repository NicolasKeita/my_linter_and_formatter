#!/usr/bin/env python3
"""Tests split into part 5."""

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
    def test_export_struct_brace_on_next_line(self):
        code = [
            "export struct ControlCommand",
            "{",
            "    double wing_rpm = 0.0;",
            "    double left_servo_angle = 0.0;",
            "    int mode = 1;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[0], "export struct ControlCommand")
        self.assertEqual(result[1], "{")
        self.assertEqual(result[2], "    double wing_rpm = 0.0;")
        self.assertEqual(result[3], "    double left_servo_angle = 0.0;")
        self.assertEqual(result[4], "    int    mode = 1;")
        self.assertEqual(result[5], "};")

    def test_namespace_level_declarations_untouched(self):
        code = [
            "export namespace sim {",
            "    struct S {",
            "        double alpha = 1.0;",
            "        int beta = 2;",
            "    };",
            "    [[nodiscard]] std::string_view name(int value);",
            "}",
        ]
        result = align_lines(code)
        self.assertEqual(result[2], "        double alpha = 1.0;")
        self.assertEqual(result[3], "        int    beta = 2;")
        self.assertEqual(result[5], "    [[nodiscard]] std::string_view name(int value);")


if __name__ == "__main__":
    unittest.main()
