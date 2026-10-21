"""Check the common filename contract through the C# command line."""

import json
import pathlib
import tempfile

from _cli_support import ROOT, CliTestCase

CASES = ROOT / "testdata" / "filename_cases.json"


class FilenameTests(CliTestCase):
    def test_shared_policy(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = pathlib.Path(temporary)
                for name in (case["left"], case["right"]):
                    (root / (name + ".cs")).write_text("class Sample {}\n", encoding="utf-8")
                result = self.run_cli("lint", root)
                self.assertEqual(result.returncode, int(case["match"]), result.stdout + result.stderr)
                self.assertEqual(result.stdout.count(": NK013 "), 2 if case["match"] else 0, result.stdout)

    def test_scopes_generated_files_and_single_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for name in ("Utility_1.cs", "nested/Utility-2.cs", "obj/Utility_3.cs", "Utility_4.g.cs"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("class Sample {}\n", encoding="utf-8")
            before = {path: path.read_bytes() for path in root.rglob("*.cs")}
            self.assertEqual(self.run_cli("lint", root).returncode, 0)
            result = self.run_cli("lint", root, "--similarity-scope", "project")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count(": NK013 "), 2)
            self.assertEqual(self.run_cli("lint", root / "Utility_1.cs").returncode, 0)
            self.assertEqual(self.run_cli("lint", root, "--similarity-scope", "invalid").returncode, 2)
            self.assertEqual(before, {path: path.read_bytes() for path in root.rglob("*.cs")})

    def test_project_compile_selection_and_grouped_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for name in ("Utility_1.cs", "Utility_2.cs", "Utility_3.cs"):
                (root / name).write_text("class Sample {}\n", encoding="utf-8")
            project = root / "Sample.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                "<TargetFramework>net10.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems>"
                '</PropertyGroup><ItemGroup><Compile Include="Utility_1.cs" /></ItemGroup></Project>',
                encoding="utf-8",
            )
            self.assertEqual(self.run_cli("lint", project).returncode, 0)
            result = self.run_cli("lint", root)
            self.assertEqual(result.stdout.count(": NK013 "), 3, result.stdout + result.stderr)
