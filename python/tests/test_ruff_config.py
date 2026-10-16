import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RuffConfigurationTests(unittest.TestCase):
    def check_source(self, source):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "sample.py"
            path.write_text(source, encoding="utf-8", newline="\n")
            checked = subprocess.run(
                [sys.executable, "-m", "nk_python", "check", str(path)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(path.read_bytes(), source.encode("utf-8"))
            return checked.returncode, checked.stdout + checked.stderr

    def test_check_ignores_only_the_disabled_rules(self):
        source = (
            "import warnings\n\n\n"
            "def factory():\n    return object()\n\n\n"
            "def with_default(value=factory()):\n    return value\n\n\n"
            "def repeated():\n    return 1\n\n\n"
            "def repeated():\n    return 2\n\n\n"
            'warnings.warn("example")\n'
            "pairs = zip([1], [2])\n"
        )
        status, output = self.check_source(source)
        self.assertEqual(status, 0, output)
        self.assertIn("All checks passed!", output)
        for rule in ("B008", "B028", "B905", "F811"):
            with self.subTest(rule=rule):
                self.assertNotIn(rule, output)

    def test_check_preserves_other_rules(self):
        source = (
            "import os\nfrom typing import List\n\n"
            "missing_name\n"
            "42\n"
            "for unused in range(2):\n"
            '    print("example")\n'
            "callbacks = []\n"
            "for value in range(2):\n"
            "    callbacks.append(lambda: value)\n"
            "identity = lambda value: value\n"
        )
        status, output = self.check_source(source)
        self.assertEqual(status, 1, output)
        for rule in ("F821", "B023", "F401", "B018", "B007", "UP035", "E731"):
            with self.subTest(rule=rule):
                self.assertRegex(output, rf": {rule}\b")


if __name__ == "__main__":
    unittest.main()
