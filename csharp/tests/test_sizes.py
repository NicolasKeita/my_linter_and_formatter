import pathlib
import tempfile

from _cli_support import CliTestCase


class SizeTests(CliTestCase):
    def test_size_limits_and_direct_file_count(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            source = target / "Large.cs"
            body = "\n".join("        System.Console.WriteLine(1);" for _ in range(41))
            source.write_text(
                "class Large\n{\n    void Run()\n    {\n"
                + body
                + "\n    }\n}\n"
                + "// "
                + "x" * 120
                + "\n"
                + "\n" * 401,
                encoding="utf-8",
            )
            for index in range(10):
                (target / f"Extra{index}.cs").write_text(f"class Extra{index} {{}}\n", encoding="utf-8")
            result = self.run_cli("lint", target)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for rule in ("NK001", "NK002", "NK003", "NK011"):
                self.assertIn(rule, result.stdout)

    def test_expression_lambda_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Lambda.cs"
            path.write_text(
                "class Example\n"
                "{\n"
                "    void Run()\n"
                "    {\n"
                "        System.Func<int, int, int, int, int, int, int> combine = "
                "(a, b, c, d, e, f) => a + b + c + d + e + f;\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("NK004", result.stdout)
