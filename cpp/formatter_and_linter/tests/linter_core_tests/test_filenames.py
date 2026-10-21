"""Filename policy parity, C++ module conventions and command line coverage."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from linter.core.filenames.comparison import reason
from linter.core.filenames.scan import check_similar_filenames

PACKAGE = Path(__file__).resolve().parents[2]
CASES = PACKAGE.parents[1] / "testdata" / "filename_cases.json"


class FilenameTests(unittest.TestCase):
    def test_shared_policy(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            with self.subTest(case=case):
                self.assertEqual(bool(reason(case["left"] + ".cpp", case["right"] + ".cpp")), case["match"])

    def test_module_prefix_and_interface_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            module = "VeryLongModuleName"
            for name in (f"{module}-Read.cpp", f"{module}-Write.cpp", f"{module}-Read.cppm"):
                (root / name).write_text(f"module {module};\n", encoding="utf-8")
            self.assertEqual(check_similar_filenames([temporary]), [])
            (root / f"{module}-Read_2.cpp").write_text(f"module {module};\n", encoding="utf-8")
            self.assertEqual(len(check_similar_filenames([temporary, temporary])), 2)

    def test_cli_scopes_status_and_read_only_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("Src/Utility_1.cpp", "Src/nested/Utility-2.cpp"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("int value = 1;\n", encoding="utf-8")
            before = {path: path.read_bytes() for path in root.rglob("*.cpp")}
            for scope in ("directory", "project"):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(PACKAGE.parent / "formatter_and_linter.py"),
                        "--check",
                        "--similarity-scope",
                        scope,
                    ],
                    cwd=root,
                    env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(result.returncode, int(scope == "project"), result.stdout + result.stderr)
                self.assertEqual(result.stderr.count("[WARN_SIMILAR_FILENAME]"), 2 if scope == "project" else 0)
            self.assertEqual(before, {path: path.read_bytes() for path in root.rglob("*.cpp")})

    def test_dotted_partition_and_interface_fallback_prefixes(self):
        for declaration in ("module VeryLong.Module:Partition;\n", "// No module declaration.\n"):
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for suffix in ("-Read.cpp", "-Write.cpp", ".cppm"):
                    (root / ("VeryLong.Module" + suffix)).write_text(declaration, encoding="utf-8")
                self.assertEqual(check_similar_filenames([temporary]), [])
