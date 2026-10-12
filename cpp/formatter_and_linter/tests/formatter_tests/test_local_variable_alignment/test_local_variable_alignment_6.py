#!/usr/bin/env python3
"""Tests split into part 6."""

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
    def test_trailing_newline_preserved(self):
        code = "void f() {\n    int a = 1;\n    long b = 2;\n    use(a, b);\n}\n"
        target = len("long") + 1
        expected = (
            "void f() {\n"
            + aligned_line("    ", "int", "a", " = 1;", target)
            + "\n"
            + aligned_line("    ", "long", "b", " = 2;", target)
            + "\n    use(a, b);\n}\n"
        )
        self.assertEqual(align_first_declaration_blocks(code), expected)


if __name__ == "__main__":
    unittest.main()
