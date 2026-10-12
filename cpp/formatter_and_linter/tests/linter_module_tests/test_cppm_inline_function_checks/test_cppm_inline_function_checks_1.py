#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.cppm_inline_function_checks import (
    MAX_CPPM_INLINE_FUNCTION_BODY_LINES,
    WARN_CPPM_INLINE_FUNCTION_TAG,
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

    def test_max_body_lines_constant(self):
        self.assertEqual(MAX_CPPM_INLINE_FUNCTION_BODY_LINES, 1)

    def test_non_cppm_files_are_ignored(self):
        cpp_file = self.write_file("Sample.cpp", "int f()\n{\n    int a = 0;\n    return a;\n}\n")
        self.assertEqual(check_cppm_inline_functions(cpp_file), [])

    def test_single_line_getter_is_allowed(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::int32_t value() const { return value_; }\n"
            "\n"
            "private:\n"
            "    std::int32_t value_ = 0;\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_single_line_setter_is_allowed(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    void setValue(std::int32_t value) { value_ = value; }\n"
            "\n"
            "private:\n"
            "    std::int32_t value_ = 0;\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_empty_body_is_allowed(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    void noop() {}\n"
            "    void alsoNoop() {\n"
            "    }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_multi_line_free_function_is_reported(self):
        file_path = self.write_cppm(
            "export std::int32_t compute(std::int32_t a, std::int32_t b)\n"
            "{\n"
            "    std::int32_t sum = a + b;\n"
            "    return sum * 2;\n"
            "}\n"
        )
        warnings = check_cppm_inline_functions(file_path)
        self.assertEqual(len(warnings), 1)
        message = warnings[0]
        self.assertIn(WARN_CPPM_INLINE_FUNCTION_TAG, message)
        self.assertIn(str(file_path), message)
        self.assertIn(":13 :", message)
        self.assertIn("'compute'", message)
        self.assertIn("2 lignes", message)


if __name__ == "__main__":
    unittest.main()
