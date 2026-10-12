#!/usr/bin/env python3
"""Tests split into part 5."""

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

    def test_constructor_with_initializer_list_is_reported(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    Sample() : x_(0), y_(1)\n"
            "    {\n"
            "        init();\n"
            "        reset();\n"
            "    }\n"
            "\n"
            "private:\n"
            "    std::int32_t x_;\n"
            "    std::int32_t y_;\n"
            "};\n"
        )
        warnings = check_cppm_inline_functions(file_path)
        self.assertEqual(len(warnings), 1)
        self.assertIn("'Sample'", warnings[0])
        self.assertIn("2 lignes", warnings[0])

    def test_constructor_with_braced_initializers_is_reported(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    Sample() : x_{0}, y_{1} {\n"
            "        init();\n"
            "        reset();\n"
            "    }\n"
            "\n"
            "private:\n"
            "    std::int32_t x_;\n"
            "    std::int32_t y_;\n"
            "};\n"
        )
        warnings = check_cppm_inline_functions(file_path)
        self.assertEqual(len(warnings), 1)
        self.assertIn("'Sample'", warnings[0])

    def test_braced_member_initializers_are_not_functions(self):
        file_path = self.write_cppm(
            "export struct Stats\n"
            "{\n"
            "    std::int32_t count{};\n"
            "    std::array<std::int32_t, 2> values{1, 2};\n"
            "    std::float64_t ratio = 0.0;\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])


if __name__ == "__main__":
    unittest.main()
