#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.cppm_inline_function_checks import (
    check_cppm_inline_functions,
)

FILE_HEADER = """/*
Filename: Src/Dummy/Sample.cppm
Description: Sample module interface used by the unit tests.

Copyright (c) 2026 Nicolas K.
All rights reserved.
*/

export module Sample;

import std;

"""


class TestCheckCppmInlineFunctions(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_file(self, file_name: str, content: str) -> Path:
        file_path = self.root / file_name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def write_cppm(self, body: str) -> Path:
        return self.write_file("Sample.cppm", FILE_HEADER + body)

    def test_multi_line_aggregate_initialization_is_not_reported(self):
        file_path = self.write_cppm(
            "export constexpr std::int32_t kTable[4] = {\n"
            "    1,\n"
            "    2,\n"
            "    3,\n"
            "    4,\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_braces_inside_line_comment_are_ignored(self):
        file_path = self.write_cppm(
            "// void fake() {\n"
            "//     int a = 0;\n"
            "// }\n"
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::int32_t value() const { return 0; } // trailing brace: }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_braces_inside_block_comment_are_ignored(self):
        file_path = self.write_cppm(
            "/*\n"
            "void alsoFake() {\n"
            "    int b = 1;\n"
            "    int c = 2;\n"
            "}\n"
            "*/\n"
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::int32_t value() const { return 0; }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_braces_inside_string_literal_are_ignored(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::string_view text() const { return \"{ not a block }\"; }\n"
            "    std::string_view escaped() const { return \"quote \\\" } here\"; }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_braces_inside_char_literal_are_ignored(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    char openBrace() const { return '{'; }\n"
            "    char closeBrace() const { return '}'; }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])


if __name__ == "__main__":
    unittest.main()
