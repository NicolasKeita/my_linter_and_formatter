import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_check_separates_linter_diagnostics_and_formatter_corrections(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.py"
            source = "import sys\nimport os\n\nvalue=1  # inline comment\n"
            path.write_text(source, encoding="utf-8")
            command = [sys.executable, "-m", "nk_python"]
            checked = subprocess.run(command + ["check", str(path)], capture_output=True, text=True, check=False)
            output = checked.stdout
            self.assertEqual(checked.returncode, 1, checked.stderr + output)
            linter, formatter = output.split("=== Formatter: corrections available via 'format' ===")
            self.assertTrue(linter.startswith("=== Linter diagnostics ==="))
            self.assertIn("F401", linter)
            self.assertIn("PY005", linter)
            self.assertNotIn("[*]", linter)
            self.assertNotIn("I001", linter)
            self.assertNotIn("would be reformatted", linter)
            self.assertIn("I001", formatter)
            self.assertIn("would be reformatted", formatter)
            self.assertNotIn("F401", formatter)
            self.assertNotIn("PY005", formatter)
            self.assertEqual(path.read_text(encoding="utf-8"), source)
            formatted = subprocess.run(command + ["format", str(path)], capture_output=True, text=True, check=False)
            self.assertEqual(formatted.returncode, 0, formatted.stderr + formatted.stdout)
            checked = subprocess.run(command + ["check", str(path)], capture_output=True, text=True, check=False)
            self.assertEqual(checked.returncode, 1, checked.stderr + checked.stdout)
            self.assertIn("F401", checked.stdout)
            self.assertIn("PY005", checked.stdout)
            self.assertNotIn("I001", checked.stdout)
            self.assertNotIn("would be reformatted", checked.stdout)

    def test_check_reports_relative_paths_without_source_excerpts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / "src"
            folder.mkdir()
            path = folder / "sample.py"
            source = "import os\n\nvalue=1  # inline comment\n"
            path.write_text(source, encoding="utf-8")
            check = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(folder)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            output = check.stdout + check.stderr
            self.assertEqual(check.returncode, 1, output)
            self.assertIn(f"{Path('src') / 'sample.py'}:1:8: F401", output)
            self.assertIn(f"{Path('src') / 'sample.py'}:3: PY005", output)
            self.assertIn("sample.py", output)
            self.assertNotIn(str(root), output)
            self.assertNotIn("import os", output)
            self.assertNotIn("inline comment", output)
            self.assertEqual(path.read_text(encoding="utf-8"), source)

    def test_check_is_read_only_and_format_fixes_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.py"
            path.write_text("value=1\n", encoding="utf-8")
            before = path.read_bytes()
            check = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 1)
            self.assertEqual(path.read_bytes(), before)
            formatted = subprocess.run(
                [sys.executable, "-m", "nk_python", "format", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(formatted.returncode, 0, formatted.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), "value = 1\n")
            checked = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)


if __name__ == "__main__":
    unittest.main()
