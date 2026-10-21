import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nk_python.structure_checks import discover


class SubdirectoryTests(unittest.TestCase):
    def test_counts_direct_empty_children_and_respects_ignored_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for number in range(8):
                (root / f"part_{number}" / "nested").mkdir(parents=True)
            for name in (".git", ".venv", ".venv-custom", "__pycache__", "build", "dist", "node_modules"):
                for number in range(9):
                    (root / name / str(number)).mkdir(parents=True)
            self.assertEqual(discover([root]), ([], []))
            (root / "ninth").mkdir()
            files, issues = discover([root, root / "part_0", root])
            self.assertEqual(files, [])
            self.assertEqual([(issue.path, issue.code) for issue in issues], [(root, "PY009")])
            self.assertIn("9 direct subdirectories (max 8)", issues[0].message)
            checked = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
            self.assertIn("PY009", checked.stdout)
            self.assertIn("Files checked: 0", checked.stdout)

    def test_check_reports_nested_limit_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "src"
            for number in range(8):
                (nested / str(number)).mkdir(parents=True)
            source = root / "sample.py"
            source.write_text("value = 1\n", encoding="utf-8", newline="\n")
            before = source.read_bytes()
            for count in (8, 9):
                if count == 9:
                    (nested / "8").mkdir()
                result = subprocess.run(
                    [sys.executable, "-m", "nk_python", "check", str(root)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, int(count > 8), result.stdout + result.stderr)
                if count > 8:
                    self.assertIn("PY009", result.stdout)
                    self.assertIn("Linter: 1 warnings", result.stdout)
                self.assertEqual(source.read_bytes(), before)
