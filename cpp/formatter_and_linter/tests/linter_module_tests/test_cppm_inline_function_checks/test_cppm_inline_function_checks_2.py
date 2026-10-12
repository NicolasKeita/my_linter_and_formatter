#!/usr/bin/env python3
"""Tests split into part 2."""

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

    def test_multi_line_method_inside_class_is_reported(self):
        file_path = self.write_cppm(
            "export class Sample\n"
            "{\n"
            "public:\n"
            "    void reset()\n"
            "    {\n"
            "        stop();\n"
            "        clear();\n"
            "    }\n"
            "};\n"
        )
        warnings = check_cppm_inline_functions(file_path)
        self.assertEqual(len(warnings), 1)
        self.assertIn(":16 :", warnings[0])
        self.assertIn("'reset'", warnings[0])

    def test_multi_line_struct_without_functions_is_not_reported(self):
        file_path = self.write_cppm(
            "export struct SimulationState\n"
            "{\n"
            "    bool fc1_alive = true;\n"
            "    bool comms_link_up = true;\n"
            "    std::float64_t comms_loss_probability = 0.0;\n"
            "    std::float64_t actuator_efficiency = 1.0;\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_multi_line_namespace_without_functions_is_not_reported(self):
        file_path = self.write_cppm(
            "export namespace sim::sample {\n"
            "\n"
            "struct First {\n"
            "    bool alive = true;\n"
            "};\n"
            "\n"
            "struct Second {\n"
            "    std::int32_t count = 0;\n"
            "};\n"
            "\n"
            "}\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])

    def test_multi_line_enum_class_is_not_reported(self):
        file_path = self.write_cppm(
            "export enum class FaultDomain\n"
            "{\n"
            "    None,\n"
            "    FC1Heartbeat,\n"
            "    CommsLink,\n"
            "};\n"
        )
        self.assertEqual(check_cppm_inline_functions(file_path), [])


if __name__ == "__main__":
    unittest.main()
