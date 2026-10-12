#!/usr/bin/env python3
"""Tests split into part 4."""

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

    def test_braces_inside_raw_string_are_ignored(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::string_view json() const { return R\"({ \"key\": {} })\"; }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_comment_only_body_is_not_reported(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    void noop()\n"
            "    {\n"
            "        // nothing to do { here }\n"
            "        /* still nothing { here } */\n"
            "    }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_blank_lines_do_not_count_as_effective_lines(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::int32_t value() const\n"
            "    {\n"
            "\n"
            "        return value_;\n"
            "\n"
            "    }\n"
            "\n"
            "private:\n"
            "    std::int32_t value_ = 0;\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_digit_separator_does_not_break_literal_parsing(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    std::int32_t value() const { return 1'000'000; }\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])


if __name__ == "__main__":
    unittest.main()
