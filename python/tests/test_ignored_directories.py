import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nk_python.structure_checks import discover


class IgnoredBuildDirectoryTests(unittest.TestCase):
    def test_build_outputs_are_ignored_at_every_level_without_hiding_source_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "src"
            source.mkdir()
            expected = []
            for name in ("binary", "objects", "build_tools"):
                path = source / name / "visible.py"
                path.parent.mkdir()
                path.write_text("value = 1\n", encoding="utf-8", newline="\n")
                expected.append(path.resolve())
            for parent in (root, source):
                for name in (
                    "bin",
                    "obj",
                    "coverage",
                    "htmlcov",
                    ".cache",
                    ".vs",
                    ".idea",
                    "demo.egg-info",
                    "cmake-build-debug",
                ):
                    for number in range(9):
                        path = parent / name / str(number) / "generated.py"
                        path.parent.mkdir(parents=True)
                        path.write_text("invalid python\n", encoding="utf-8")
            files, issues = discover([root])
            self.assertEqual(files, sorted(expected))
            self.assertEqual(issues, [])
            before = {path: path.read_bytes() for path in root.rglob("*.py")}
            for command in ("format", "check"):
                result = subprocess.run(
                    [sys.executable, "-m", "nk_python", command, str(root)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({path: path.read_bytes() for path in before}, before)
