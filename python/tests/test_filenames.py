"""Shared filename policy and Python discovery/CLI regression coverage."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nk_python.filenames import find_similar
from nk_python.filenames.comparison import reason
from nk_python.structure_checks import discover

CASES = Path(__file__).resolve().parents[2] / "testdata" / "filename_cases.json"


class FilenameTests(unittest.TestCase):
    def test_shared_policy(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            with self.subTest(case=case):
                self.assertEqual(bool(reason(case["left"] + ".py", case["right"] + ".py")), case["match"])

    def test_roles_scopes_exclusions_and_duplicate_roots(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("Utility.py", "Utility.pyi", "nested/Utility_2.py", "build/Utility_3.py"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            self.assertEqual(discover([root])[1], [])
            issues = discover([root, root / "nested", root], similarity_scope="project")[1]
            self.assertEqual([issue.code for issue in issues], ["PY010", "PY010"])
            self.assertEqual(find_similar([root / "Utility.py"]), [])
            with self.assertRaises(ValueError):
                find_similar([], "invalid")

    def test_cli_reports_each_file_once_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("Utility_1.py", "Utility_2.py", "Utility_3.py"):
                (root / name).write_text("value = 1\n", encoding="utf-8")
            before = {path.name: path.read_bytes() for path in root.iterdir()}
            result = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count(": PY010 "), 3)
            self.assertEqual(before, {path.name: path.read_bytes() for path in root.iterdir()})

    def test_matches_do_not_spread_transitively_and_exact_cross_directory_names_are_allowed(self):
        root = Path(tempfile.gettempdir()) / "filename-policy"
        names = ("abcdefghijklmnopqrst.py", "xyzdefghijklmnopqrst.py", "xyzabcghijklmnopqrst.py")
        matches = dict(find_similar([root / name for name in names]))
        self.assertEqual(len(matches), 3)
        self.assertNotIn(names[2], matches[(root / names[0]).resolve()])
        self.assertEqual(find_similar([root / "one/index.py", root / "two/index.py"], "project"), [])
