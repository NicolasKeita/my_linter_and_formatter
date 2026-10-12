#!/usr/bin/env python3
"""Tests split into part 4."""

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
    def test_multiple_declarators_are_untouched(self):
        code = [
            "struct S {",
            "    int a = 1, b = 2;",
            "    long_name c = 3;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    int a = 1, b = 2;")
        self.assertEqual(result[2], "    long_name c = 3;")

    def test_wrapped_declaration_breaks_block(self):
        code = [
            "struct S {",
            "    double alpha = 1.0;",
            "    long wrapped_value =",
            "        2.0;",
            "    int beta = 3;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result, code)

    def test_block_is_skipped_when_line_would_exceed_limit(self):
        code = [
            "struct S {",
            "    double alpha = 1.0;",
            "    int beta = 22222;",
            "};",
        ]
        result = align_member_variables("\n".join(code) + "\n", max_line_length=20)
        self.assertEqual(result, "\n".join(code) + "\n")

    def test_pass_is_idempotent(self):
        code = (
            "struct S {\n"
            "    double alpha = 1.0;\n"
            "    int beta = 2;\n"
            "    std::uint64_t count = 0;\n"
            "};\n"
        )
        once = align_member_variables(code)
        self.assertEqual(align_member_variables(once), once)

    def test_class_with_methods_and_members(self):
        code = [
            "class CommsBus {",
            "public:",
            "    explicit CommsBus(std::uint64_t seed = 42);",
            "",
            "    void seed(std::uint64_t seed);",
            "",
            "private:",
            "    std::mt19937_64 generator_;",
            "    bool link_up_ = true;",
            "    double loss_probability_ = 0.0;",
            "    std::uint64_t sequence_ = 0;",
            "};",
        ]
        result = align_lines(code)
        target = len("std::mt19937_64") + 1
        self.assertEqual(result[2], "    explicit CommsBus(std::uint64_t seed = 42);")
        self.assertEqual(result[4], "    void seed(std::uint64_t seed);")
        self.assertEqual(result[7], member_line("    ", "std::mt19937_64", "generator_", ";", target))
        self.assertEqual(result[8], member_line("    ", "bool", "link_up_", " = true;", target))
        self.assertEqual(result[9], member_line("    ", "double", "loss_probability_", " = 0.0;", target))
        self.assertEqual(result[10], member_line("    ", "std::uint64_t", "sequence_", " = 0;", target))

    def test_enum_body_is_untouched(self):
        code = [
            "enum class Mode {",
            "    None = 0,",
            "    Auto = 1,",
            "};",
        ]
        self.assertEqual(align_lines(code), code)


if __name__ == "__main__":
    unittest.main()
