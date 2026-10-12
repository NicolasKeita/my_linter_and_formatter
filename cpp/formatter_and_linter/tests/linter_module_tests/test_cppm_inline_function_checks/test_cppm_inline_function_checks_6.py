#!/usr/bin/env python3
"""Tests split into part 6."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.cppm_inline_function_checks import (
    check_cppm_inline_function_bodies,
    check_cppm_inline_functions,
    format_cppm_inline_function_message,
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

    def test_multiple_violations_are_reported_in_line_order(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    void second()\n"
            "    {\n"
            "        a();\n"
            "        b();\n"
            "    }\n"
            "};\n"
            "\n"
            "export int first()\n"
            "{\n"
            "    int x = 1;\n"
            "    return x;\n"
            "}\n"
        )
        warnings = check_cppm_inline_functions(file_path)
        self.assertEqual(len(warnings), 2)
        self.assertIn("'second'", warnings[0])
        self.assertIn("'first'", warnings[1])

    def test_code_based_entry_point_matches_file_based_one(self):
        body = (
            "export int compute()\n"
            "{\n"
            "    int a = 1;\n"
            "    return a;\n"
            "}\n"
        )
        file_path = self.write_cppm(body)
        violations = check_cppm_inline_function_bodies(FILE_HEADER + body)
        self.assertEqual(len(violations), 1)
        function_name, start_line, body_lines = violations[0]
        self.assertEqual(function_name, "compute")
        self.assertEqual(body_lines, 2)
        self.assertEqual(len(check_cppm_inline_functions(file_path)), 1)
        self.assertIn(f":{start_line} :", check_cppm_inline_functions(file_path)[0])

    def test_message_format_matches_specification(self):
        message = format_cppm_inline_function_message("Src/App/Application.cppm", "Run", 42, 3)
        self.assertEqual(
            message,
            "[WARN_CPPM_INLINE_FUNCTION] Src/App/Application.cppm:42 : "
            "la fonction 'Run' possède un corps de 3 lignes effectives "
            "dans l'interface de module (max : 1). "
            "Déplace l'implémentation dans un fichier .cpp.",
        )


if __name__ == "__main__":
    unittest.main()
