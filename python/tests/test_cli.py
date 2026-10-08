import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
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
