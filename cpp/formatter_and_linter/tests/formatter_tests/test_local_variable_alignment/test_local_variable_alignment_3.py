#!/usr/bin/env python3
"""Tests split into part 3."""

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
    def test_empty_function_body_is_unchanged(self):
        code = [
            "void f() {",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")

    def test_allman_brace_on_own_line(self):
        code = [
            "void f()",
            "{",
            "    const std::uint64_t a = 1;",
            "    const std::uint64_t bbb = 2;",
            "",
            "    use(a, bbb);",
            "}",
        ]
        target = len("const std::uint64_t") + 1
        expected = [
            "void f()",
            "{",
            aligned_line("    ", "const std::uint64_t", "a", " = 1;", target),
            aligned_line("    ", "const std::uint64_t", "bbb", " = 2;", target),
            "",
            "    use(a, bbb);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_function_inside_namespace_is_aligned_and_indented(self):
        code = [
            "namespace sim {",
            "void generate() {",
            "    int alpha = 1;",
            "    long_name beta = 2;",
            "",
            "    run(alpha, beta);",
            "}",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "namespace sim {",
            "void generate() {",
            aligned_line("    ", "int", "alpha", " = 1;", target),
            aligned_line("    ", "long_name", "beta", " = 2;", target),
            "",
            "    run(alpha, beta);",
            "}",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_leading_blank_after_brace_is_skipped(self):
        code = [
            "void f() {",
            "",
            "    int a = 1;",
            "    long_name b = 2;",
            "",
            "    use(a, b);",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "void f() {",
            "",
            aligned_line("    ", "int", "a", " = 1;", target),
            aligned_line("    ", "long_name", "b", " = 2;", target),
            "",
            "    use(a, b);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_lone_multiline_declaration_is_left_alone(self):
        code = [
            "void f() {",
            "    SomeType x = make(",
            "        1, 2);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(code) + "\n")


if __name__ == "__main__":
    unittest.main()
