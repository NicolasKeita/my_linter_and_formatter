#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.spacing.comment_function_formatter import format_comment_function_spacing


def fmt(code: str) -> str:
    return format_comment_function_spacing(code)


class TestCommentFunctionSpacing(unittest.TestCase):
    def test_block_comment_closing_with_no_blank_line_before_function(self):
        code = (
            "/*\n"
            "  Description...\n"
            "*/\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), code)

    def test_block_comment_with_extra_blank_line_is_collapsed(self):
        code = (
            "/*\n"
            "  Description...\n"
            "*/\n"
            "\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        expected = (
            "/*\n"
            "  Description...\n"
            "*/\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), expected)

    def test_block_comment_with_multiple_blank_lines_is_collapsed(self):
        code = (
            "/*\n"
            "  Description...\n"
            "*/\n"
            "\n"
            "\n"
            "\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        expected = (
            "/*\n"
            "  Description...\n"
            "*/\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), expected)

    def test_single_line_comment_before_function(self):
        code = (
            "// Description...\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), code)

    def test_single_line_block_comment_before_function(self):
        code = (
            "/* Description... */\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), code)

    def test_code_before_function_gets_blank_line(self):
        code = (
            "int x = 5;\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        expected = (
            "int x = 5;\n"
            "\n"
            "static int foo()\n"
            "{\n"
            "    return 0;\n"
            "}"
        )
        self.assertEqual(fmt(code), expected)


if __name__ == "__main__":
    unittest.main()
