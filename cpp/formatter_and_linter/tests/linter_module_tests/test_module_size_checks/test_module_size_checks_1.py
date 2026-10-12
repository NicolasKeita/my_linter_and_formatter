#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.module_size_checks import (
    MAX_IMPLEMENTATION_FILES_PER_MODULE,
    SUB_MODULE_PLACEHOLDER,
    check_module_implementation_counts,
)


class TestCheckModuleImplementationCounts(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_source_file(self, directory: str, file_name: str, content: str = "") -> None:
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, file_name), "w", encoding="utf-8") as handle:
            handle.write(content)

    def write_prefixed_implementations(self, directory: str, prefix: str, count: int) -> None:
        for index in range(count):
            self.write_source_file(directory, prefix + "-" + str(index) + ".cpp")

    def test_max_implementation_files_constant(self):
        self.assertEqual(MAX_IMPLEMENTATION_FILES_PER_MODULE, 8)

    def test_group_at_limit_is_valid(self):
        directory = os.path.join(self.root, "Tests", "Small")
        self.write_prefixed_implementations(directory, "Alpha-Beta", MAX_IMPLEMENTATION_FILES_PER_MODULE)
        self.assertEqual(check_module_implementation_counts([directory]), [])

    def test_group_above_limit_is_reported(self):
        directory = os.path.join(self.root, "Tests", "Big")
        self.write_prefixed_implementations(directory, "Alpha-Beta", MAX_IMPLEMENTATION_FILES_PER_MODULE + 1)
        violations = check_module_implementation_counts([directory])
        self.assertEqual(violations, [
            (
                "Alpha::Beta",
                MAX_IMPLEMENTATION_FILES_PER_MODULE + 1,
                "Alpha::Beta::" + SUB_MODULE_PLACEHOLDER,
            ),
        ])

    def test_interface_files_are_not_counted(self):
        directory = os.path.join(self.root, "Tests", "Interfaces")
        self.write_prefixed_implementations(directory, "Alpha-Beta", MAX_IMPLEMENTATION_FILES_PER_MODULE)
        for index in range(3):
            self.write_source_file(directory, "Alpha-Beta-Part" + str(index) + ".cppm")
        self.assertEqual(check_module_implementation_counts([directory]), [])

    def test_nested_sub_prefix_counts_in_parent_group(self):
        directory = os.path.join(self.root, "Tests", "Sil", "Observability")
        telemetry_directory = os.path.join(directory, "Telemetry")
        self.write_prefixed_implementations(directory, "SilScenarios-Observability", 8)
        self.write_prefixed_implementations(telemetry_directory, "SilScenarios-Observability-Telemetry", 2)
        violations = check_module_implementation_counts([directory])
        self.assertEqual(violations, [
            (
                "SilScenarios::Observability",
                10,
                "SilScenarios::Observability::Telemetry",
            ),
        ])

    def test_non_source_files_are_ignored(self):
        directory = os.path.join(self.root, "Tests", "Docs")
        os.makedirs(directory, exist_ok=True)
        for name in ("Readme.md", "CMakeLists.txt", "notes.log"):
            with open(os.path.join(directory, name), "w", encoding="utf-8"):
                pass
        self.assertEqual(check_module_implementation_counts([directory]), [])

    def test_only_deepest_exceeding_group_is_reported(self):
        directory = os.path.join(self.root, "Tests", "Sil")
        observability_directory = os.path.join(directory, "Observability")
        telemetry_directory = os.path.join(observability_directory, "Telemetry")
        self.write_prefixed_implementations(directory, "SilScenarios-Direct", 2)
        self.write_prefixed_implementations(observability_directory, "SilScenarios-Observability", 8)
        self.write_prefixed_implementations(telemetry_directory, "SilScenarios-Observability-Telemetry", 4)
        violations = check_module_implementation_counts([directory])
        self.assertEqual(violations, [
            (
                "SilScenarios::Observability",
                12,
                "SilScenarios::Observability::Telemetry",
            ),
        ])

    def test_module_declaration_groups_single_segment_files(self):
        directory = os.path.join(self.root, "Tests", "Modules")
        for index in range(MAX_IMPLEMENTATION_FILES_PER_MODULE + 1):
            self.write_source_file(directory, "Unit" + str(index) + ".cpp", "module BigThing;\n")
        violations = check_module_implementation_counts([directory])
        self.assertEqual(violations, [
            (
                "BigThing",
                MAX_IMPLEMENTATION_FILES_PER_MODULE + 1,
                "BigThing::" + SUB_MODULE_PLACEHOLDER,
            ),
        ])


if __name__ == "__main__":
    unittest.main()
