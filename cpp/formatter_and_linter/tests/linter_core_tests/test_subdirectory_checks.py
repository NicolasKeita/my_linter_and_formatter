"""Regression tests for direct subdirectory limits and CLI reporting."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from linter.core.directory_checks import check_directory_subdirectory_counts

PACKAGE = Path(__file__).resolve().parents[2]


class SubdirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def create_children(self, root, count):
        for number in range(count):
            (root / f"part_{number}").mkdir(parents=True, exist_ok=True)

    def test_eight_direct_children_are_allowed_regardless_of_descendants_and_files(self):
        self.create_children(self.root, 8)
        for child in self.root.iterdir():
            (child / "nested").mkdir()
        for number in range(9):
            (self.root / f"file_{number}.cpp").touch()
        self.assertEqual(check_directory_subdirectory_counts([str(self.root)]), [])

    def test_ninth_empty_child_is_reported_without_source_files(self):
        self.create_children(self.root, 9)
        self.assertEqual(check_directory_subdirectory_counts([str(self.root)]), [(str(self.root), 9)])

    def test_nested_violations_are_sorted_and_overlapping_roots_are_deduplicated(self):
        for name in ("Z", "A"):
            self.create_children(self.root / name, 9)
        violations = check_directory_subdirectory_counts(
            [str(self.root), str(self.root / "A"), str(self.root / "missing")]
        )
        self.assertEqual(violations, [(str(self.root / "A"), 9), (str(self.root / "Z"), 9)])

    def test_check_and_recursive_cli_enforce_limit(self):
        source_root = self.root / "Src"
        self.create_children(source_root, 8)
        source = source_root / "Sample.cpp"
        source.write_text("int value = 1;\n", encoding="utf-8")
        environment = dict(os.environ, PYTHONIOENCODING="utf-8")
        for count in (8, 9):
            if count == 9:
                (source_root / "part_8").mkdir()
            for options in (["--check"], ["-r", "-i"]):
                with self.subTest(count=count, options=options):
                    result = subprocess.run(
                        [sys.executable, str(PACKAGE.parent / "formatter_and_linter.py"), *options],
                        cwd=self.root,
                        env=environment,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        check=False,
                    )
                    self.assertEqual(result.returncode, int(count > 8), result.stdout + result.stderr)
                    if count > 8:
                        self.assertIn("9 direct subdirectories (max: 8)", result.stderr)
                    self.assertEqual(source.read_text(encoding="utf-8"), "int value = 1;\n")
        source.unlink()
        result = subprocess.run(
            [sys.executable, str(PACKAGE.parent / "formatter_and_linter.py"), "--check"],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("9 direct subdirectories (max: 8)", result.stderr)
