#!/usr/bin/env python3
"""Tests split into part 3."""

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
    def test_tab_indentation_is_preserved(self):
        code = "\n".join([
            "struct S {",
            "\tint a = 1;",
            "\tlong_name b = 2;",
            "};",
            "",
        ])
        expected = "\n".join([
            "struct S {",
            "\tint       a = 1;",
            "\tlong_name b = 2;",
            "};",
            "",
        ])
        self.assertEqual(align_member_variables(code), expected)

    def test_nested_struct_blocks_are_independent(self):
        code = [
            "class Outer {",
            "private:",
            "    struct Inner {",
            "        int a = 1;",
            "        long_name b = 2;",
            "        long_name c = 3;",
            "    };",
            "    int d = 4;",
            "    long_name e = 5;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[3], "        int       a = 1;")
        self.assertEqual(result[4], "        long_name b = 2;")
        self.assertEqual(result[5], "        long_name c = 3;")
        self.assertEqual(result[7], "    int       d = 4;")
        self.assertEqual(result[8], "    long_name e = 5;")

    def test_declaration_without_initializer(self):
        code = [
            "struct S {",
            "    std::mutex mutex;",
            "    int a = 1;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    std::mutex mutex;")
        self.assertEqual(result[2], "    int        a = 1;")

    def test_array_member(self):
        code = [
            "struct S {",
            "    std::uint8_t buffer[64];",
            "    int a = 1;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    std::uint8_t buffer[64];")
        self.assertEqual(result[2], "    int          a = 1;")

    def test_template_type_with_parentheses(self):
        code = [
            "struct S {",
            "    std::function<void(int)> callback_;",
            "    std::function<bool(double)> predicate_ = nullptr;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    std::function<void(int)>    callback_;")
        self.assertEqual(result[2], "    std::function<bool(double)> predicate_ = nullptr;")

    def test_pointer_and_reference_styles_are_preserved(self):
        code = [
            "struct S {",
            "    const AircraftState* ptr = nullptr;",
            "    const AircraftState &ref = *state;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], "    const AircraftState*  ptr = nullptr;")
        self.assertEqual(result[2], "    const AircraftState & ref = *state;")

    def test_string_literal_with_slashes(self):
        code = [
            "struct S {",
            '    std::string endpoint = "http://127.0.0.1:8080";',
            "    int a = 1;",
            "};",
        ]
        result = align_lines(code)
        self.assertEqual(result[1], '    std::string endpoint = "http://127.0.0.1:8080";')
        self.assertEqual(result[2], "    int         a = 1;")


if __name__ == "__main__":
    unittest.main()
