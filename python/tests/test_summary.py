import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SummaryTests(unittest.TestCase):
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
            summary, details = checked.stdout.split("=== Linter diagnostics ===")
            self.assertTrue(summary.startswith("=== Check summary ==="))
            self.assertIn("Files checked: 51", summary)
            self.assertIn("Linter: 103 diagnostics", summary)
            self.assertIn("Formatter: 51 import diagnostics; 51 files to reformat", summary)
            self.assertIn("PY008", details)
            self.assertEqual(checked.stdout.count("=== Check summary ==="), 1)
            self.assertTrue(all(path.read_text(encoding="utf-8") == source for path in root.glob("*.py")))
