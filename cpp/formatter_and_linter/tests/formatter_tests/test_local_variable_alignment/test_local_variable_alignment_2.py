#!/usr/bin/env python3
"""Tests split into part 2."""

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
    def test_blank_line_ends_block(self):
        code = [
            "void f() {",
            "    int a = 1;",
            "    long_name b = 2;",
            "",
            "    int c = 3;",
            "    long_name d = 4;",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "void f() {",
            aligned_line("    ", "int", "a", " = 1;", target),
            aligned_line("    ", "long_name", "b", " = 2;", target),
            "",
            "    int c = 3;",
            "    long_name d = 4;",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_function_call_is_not_aligned(self):
        code = [
            "void f() {",
            "    apply_fault(fault_roll);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")

    def test_constructor_call_form_is_supported(self):
        long_type = "std::uniform_real_distribution<std::float64_t>"
        code = [
            "void f() {",
            "    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);",
            "    const std::uint64_t roll = generator() % 6;",
            "",
            "    apply(unit, roll);",
            "}",
        ]
        target = len(long_type) + 1
        expected = [
            "void f() {",
            aligned_line("    ", long_type, "unit", "(0.0, 1.0);", target),
            aligned_line("    ", "const std::uint64_t", "roll", " = generator() % 6;", target),
            "",
            "    apply(unit, roll);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_control_structure_body_is_not_aligned(self):
        code = [
            "void f() {",
            "    if (cond) {",
            "        int a = 1;",
            "        long_name b = 2;",
            "    }",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")

    def test_lambda_declaration_is_aligned_with_peers(self):
        code = [
            "void f() {",
            "    auto reset = [](int x) { return x; };",
            "    int a = 1;",
            "    long_name b = 2;",
            "",
            "    use();",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "void f() {",
            aligned_line("    ", "auto", "reset", " = [](int x) { return x; };", target),
            aligned_line("    ", "int", "a", " = 1;", target),
            aligned_line("    ", "long_name", "b", " = 2;", target),
            "",
            "    use();",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_struct_body_is_not_aligned(self):
        code = [
            "struct S {",
            "    int a = 1;",
            "    long_name b = 2;",
            "};",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")


if __name__ == "__main__":
    unittest.main()
