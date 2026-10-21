import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SummaryTests(unittest.TestCase):
    def test_success_is_reported_once_only_when_all_checks_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for number in range(51):
                (root / f"sample_{number}.py").write_text("value = 1\n", encoding="utf-8", newline="\n")
            command = [sys.executable, "-m", "nk_python", "check", str(root)]
            checked = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(checked.returncode, 1, checked.stderr + checked.stdout)
            self.assertIn("Linter: 1 warnings", checked.stdout)
            self.assertIn("PY008", checked.stdout)
            self.assertNotIn("All checks passed!", checked.stdout)
            checked = subprocess.run(command + ["--max-files", "51"], capture_output=True, text=True, check=False)
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
            self.assertEqual(checked.stdout.count("All checks passed!"), 1)
            summary, details = checked.stdout.split("=== Linter diagnostics ===")
            self.assertIn("All checks passed!", summary)
            _, formatter = details.split("=== Formatter: corrections available via 'format' ===")
            self.assertEqual(formatter.strip(), "51 files already formatted")

    def test_summary_counts_all_batches_and_structure_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = "import sys\nimport os\n\nvalue=1\n"
            for number in range(51):
                (root / f"sample_{number}.py").write_text(source, encoding="utf-8")
            checked = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 1, checked.stderr + checked.stdout)
            self.assertNotIn("All checks passed!", checked.stdout)
            summary, details = checked.stdout.split("=== Linter diagnostics ===")
            self.assertTrue(summary.startswith("=== Check summary ==="))
            self.assertIn("Files checked: 51", summary)
            self.assertIn("Linter: 103 warnings", summary)
            self.assertIn("Formatter: 51 import diagnostics; 51 files to reformat", summary)
            self.assertIn("PY008", details)
            self.assertEqual(details.count("51 files would be reformatted"), 1)
            self.assertNotIn("50 files would be reformatted", details)
            self.assertEqual(checked.stdout.count("=== Check summary ==="), 1)
            self.assertTrue(all(path.read_text(encoding="utf-8") == source for path in root.glob("*.py")))

    def test_formatter_totals_mixed_batches_for_check_and_format(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for number in range(101):
                source = "value=1\n" if number % 2 == 0 else "value = 1\n"
                (root / f"sample_{number:03}.py").write_text(source, encoding="utf-8", newline="\n")
            command = [sys.executable, "-m", "nk_python"]
            checked = subprocess.run(
                command + ["check", str(root), "--max-files", "101"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 1, checked.stderr + checked.stdout)
            _, formatter = checked.stdout.split("=== Formatter: corrections available via 'format' ===")
            self.assertEqual(formatter.splitlines()[-1], "51 files would be reformatted, 50 files already formatted")
            self.assertEqual(formatter.count("files would be reformatted"), 1)
            self.assertEqual(formatter.count("files already formatted"), 1)
            formatted = subprocess.run(command + ["format", str(root)], capture_output=True, text=True, check=False)
            self.assertEqual(formatted.returncode, 0, formatted.stderr + formatted.stdout)
            self.assertEqual(formatted.stdout.splitlines()[-1], "51 files reformatted, 50 files left unchanged")
            self.assertEqual(formatted.stdout.count("files reformatted"), 1)
            self.assertTrue(all(path.read_text(encoding="utf-8") == "value = 1\n" for path in root.glob("*.py")))
