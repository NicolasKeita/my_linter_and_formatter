#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.module.module_filename_checks import check_module_filename_convention


class TestCheckModuleFilenameConvention(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_module_files(self, directory: str, file_names) -> None:
        os.makedirs(directory, exist_ok=True)
        for file_name in file_names:
            with open(os.path.join(directory, file_name), "w", encoding="utf-8"):
                pass

    def write_file(self, directory: str, file_name: str, content: str) -> None:
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, file_name), "w", encoding="utf-8") as handle:
            handle.write(content)

    def test_module_declaration_with_single_implementation_reports_wrong_name(self):
        directory = os.path.join(self.root, "Src", "Utils")
        self.create_module_files(directory, ["Logger.cppm"])
        self.write_file(directory, "Helper.cpp", "module Logger;\n\nimport std;\n")
        violations = check_module_filename_convention([directory])
        self.assertEqual(len(violations), 1)
        self.assertTrue(violations[0][0].endswith("Helper.cpp"))
        self.assertIn("must be named 'Logger.cpp'", violations[0][1])

    def test_module_declaration_inside_comment_is_ignored(self):
        directory = os.path.join(self.root, "Src", "Embedded")
        self.write_file(directory, "Notes.cpp",
                        "/*\nDescription: talks about module HilRunner in prose.\n*/\n")
        self.create_module_files(directory, ["HilRunner.cppm"])
        self.assertEqual(check_module_filename_convention([directory]), [])

    def test_unrelated_files_are_ignored(self):
        directory = os.path.join(self.root, "Src", "Root")
        self.create_module_files(directory, ["main.cpp", "TestHarness.cppm", "TestHarness.cpp"])
        self.assertEqual(check_module_filename_convention([directory]), [])

    def test_implementation_may_live_elsewhere(self):
        interface_dir = os.path.join(self.root, "Src", "App")
        other_dir = os.path.join(self.root, "Src", "Elsewhere")
        self.create_module_files(interface_dir, ["Application.cppm"])
        self.create_module_files(other_dir, ["Application.cpp"])
        self.assertEqual(check_module_filename_convention([interface_dir]), [])

    def test_violations_are_sorted_by_path(self):
        dir_a = os.path.join(self.root, "Src", "Aaa")
        dir_b = os.path.join(self.root, "Src", "Bbb")
        self.create_module_files(dir_a, ["ModuleA.cppm", "ModuleA-Core.cpp"])
        self.create_module_files(dir_b, ["ModuleB.cppm"])
        violations = check_module_filename_convention([dir_b, dir_a])
        self.assertEqual(
            [file_path for file_path, _ in violations],
            [os.path.join(dir_a, "ModuleA-Core.cpp")],
        )


if __name__ == "__main__":
    unittest.main()
