import pathlib
import tempfile

from _cli_support import CliTestCase


class SyntaxTests(CliTestCase):
    def test_lint_uses_csharp_syntax(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Broken.cs"
            path.write_text(
                "class Broken\n"
                "{\n"
                "    int first, second;\n"
                "    int Compute(int a, int b, int c, int d, int e, int f)\n"
                "    {\n"
                "        // inside\n"
                "        int result = a;\n"
                "        return result;\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for rule in ("NK004", "NK005", "NK006", "NK008", "NK009"):
                self.assertIn(rule, result.stdout)
            self.assertNotIn("NK000", result.stdout)

    def test_string_is_not_a_comment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Clean.cs"
            path.write_text(
                'class Clean\n{\n    string Url()\n    {\n        return "https://example.test//path";\n    }\n}\n',
                encoding="utf-8",
            )
            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_global_using_is_not_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Imports.cs"
            path.write_text("global using System;\n", encoding="utf-8")
            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
