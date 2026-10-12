#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.member_alignment_formatter import (
    align_member_variables,
    format_member_alignment_for_file,
)


def align_lines(lines, **kwargs):
    return align_member_variables("\n".join(lines) + "\n", **kwargs).splitlines()


def member_line(indent, type_part, name, rest, target):
    return indent + type_part + " " * (target - len(type_part)) + name + rest


class TestMemberAlignment(unittest.TestCase):
    def test_method_breaks_block(self):
        code = [
            "struct S {",
            "    int a = 1;",
            "    long_name b = 2;",
            "    void reset();",
            "    double c = 3.0;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    int       a = 1;")
        self.assertEqual(result[2], "    long_name b = 2;")
        self.assertEqual(result[3], "    void reset();")
        self.assertEqual(result[4], "    double c = 3.0;")

    def test_preprocessor_directive_breaks_block(self):
        code = [
            "struct S {",
            "    int a = 1;",
            "#define LIMIT 10",
            "    long_name b = 2;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    int a = 1;")
        self.assertEqual(result[2], "#define LIMIT 10")
        self.assertEqual(result[3], "    long_name b = 2;")

    def test_trailing_comment_is_preserved(self):
        code = [
            "struct S {",
            "    double alpha = 1.0;   // first",
            "    int beta = 2;  // second",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    double alpha = 1.0; // first")
        self.assertEqual(result[2], "    int    beta = 2; // second")

    def test_comment_line_does_not_break_block(self):
        code = [
            "struct S {",
            "    int a = 1;",
            "    // note about b",
            "    long_name b = 2;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    int       a = 1;")
        self.assertEqual(result[2], "    // note about b")
        self.assertEqual(result[3], "    long_name b = 2;")

    def test_block_comment_does_not_break_block(self):
        code = [
            "struct S {",
            "    int a = 1;",
            "    /*",
            "    Documentation of b.",
            "    */",
            "    long_name b = 2;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    int       a = 1;")
        self.assertEqual(result[2], "    /*")
        self.assertEqual(result[3], "    Documentation of b.")
        self.assertEqual(result[4], "    */")
        self.assertEqual(result[5], "    long_name b = 2;")

    def test_only_cppm_files_are_processed(self):
        code = (
            "struct S {\n"
            "    double alpha = 1.0;\n"
            "    int beta = 2;\n"
            "};\n"
        )
        aligned = (
            "struct S {\n"
            "    double alpha = 1.0;\n"
            "    int    beta = 2;\n"
            "};\n"
        )
        self.assertEqual(format_member_alignment_for_file("Src/Module.cpp", code), code)
        self.assertEqual(format_member_alignment_for_file("Src/Module.hpp", code), code)
        self.assertEqual(format_member_alignment_for_file("Src/Module.h", code), code)
        self.assertEqual(format_member_alignment_for_file("Src/Module", code), code)
        self.assertEqual(format_member_alignment_for_file("Src/Module.cppm", code), aligned)
        self.assertEqual(format_member_alignment_for_file("Src/Module.CPPM", code), aligned)
        self.assertEqual(align_member_variables(code), aligned)


if __name__ == "__main__":
    unittest.main()
