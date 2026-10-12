#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.module_size_checks import (
    MAX_IMPLEMENTATION_FILES_PER_MODULE,
    SUB_MODULE_PLACEHOLDER,
    check_module_implementation_counts,
    format_module_too_large_message,
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

    def test_module_declaration_inside_comments_is_ignored(self):
        directory = os.path.join(self.root, "Tests", "Comments")
        commented_content = (
            "/*\n"
            "Filename: Gamma.cpp\n"
            "module Ghost;\n"
            "*/\n"
            "\n"
            "// module GhostTwo;\n"
            "\n"
            "module RealModule;\n"
        )
        self.write_source_file(directory, "Gamma.cpp", commented_content)
        self.write_source_file(directory, "Delta.cpp", "module RealModule;\n")
        self.assertEqual(check_module_implementation_counts([directory]), [])

    def test_partition_module_uses_base_module_name(self):
        directory = os.path.join(self.root, "Tests", "Partitions")
        self.write_source_file(directory, "Unit0.cpp", "module Parted:Impl;\n")
        for index in range(1, MAX_IMPLEMENTATION_FILES_PER_MODULE + 1):
            self.write_source_file(directory, "Unit" + str(index) + ".cpp", "module Parted;\n")
        violations = check_module_implementation_counts([directory])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], "Parted")
        self.assertEqual(violations[0][1], MAX_IMPLEMENTATION_FILES_PER_MODULE + 1)

    def test_violations_are_sorted_by_label(self):
        first = os.path.join(self.root, "Tests", "Zzz")
        second = os.path.join(self.root, "Tests", "Aaa")
        self.write_prefixed_implementations(first, "Zzz-Yyy", MAX_IMPLEMENTATION_FILES_PER_MODULE + 1)
        self.write_prefixed_implementations(second, "Aaa-Bbb", MAX_IMPLEMENTATION_FILES_PER_MODULE + 1)
        violations = check_module_implementation_counts([first, second])
        self.assertEqual(
            [label for label, _, _ in violations],
            ["Aaa::Bbb", "Zzz::Yyy"],
        )

    def test_module_declaration_overrides_filename_prefix(self):
        directory = os.path.join(self.root, "Tests", "Renamed")
        for index in range(4):
            self.write_source_file(
                directory, "Other-Area-Unit" + str(index) + ".cpp", "module SilScenarios;\n"
            )
        self.write_prefixed_implementations(directory, "SilScenarios", 5)
        violations = check_module_implementation_counts([directory])
        self.assertEqual(violations, [
            (
                "SilScenarios",
                MAX_IMPLEMENTATION_FILES_PER_MODULE + 1,
                "SilScenarios::" + SUB_MODULE_PLACEHOLDER,
            ),
        ])

    def test_distinct_module_declarations_are_grouped_separately(self):
        directory = os.path.join(self.root, "Tests", "Split")
        for index in range(5):
            self.write_source_file(directory, "Alpha-Area-Unit" + str(index) + ".cpp", "module Alpha;\n")
            self.write_source_file(directory, "Beta-Area-Unit" + str(index) + ".cpp", "module Beta;\n")
        self.assertEqual(check_module_implementation_counts([directory]), [])

    def test_message_format_matches_specification(self):
        message = format_module_too_large_message(
            "SilScenarios::Observability",
            10,
            "SilScenarios::Observability::Telemetry",
        )
        self.assertEqual(
            message,
            "[WARN_MODULE_TOO_LARGE] Le module/namespace 'SilScenarios::Observability' "
            "compte 10 fichiers d'implémentation (seuil : 8). "
            "Pense à le subdiviser en sous-modules "
            "(ex : 'SilScenarios::Observability::Telemetry').",
        )


if __name__ == "__main__":
    unittest.main()
