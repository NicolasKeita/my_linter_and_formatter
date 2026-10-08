import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PROJECT = ROOT / "csharp" / "NkLint.csproj"


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["dotnet", "build", str(PROJECT), "--nologo", "-v:q"],
                       cwd=ROOT, check=True, capture_output=True, text=True)

    def run_cli(self, command, path):
        return subprocess.run(
            ["dotnet", "run", "--no-build", "--project", str(PROJECT), "--",
             command, str(path)],
            cwd=ROOT, capture_output=True, text=True,
        )

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
                "}\n", encoding="utf-8")

            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for rule in ("NK004", "NK005", "NK006", "NK008", "NK009"):
                self.assertIn(rule, result.stdout)
            self.assertNotIn("NK000", result.stdout)

    def test_string_is_not_a_comment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Clean.cs"
            path.write_text(
                "class Clean\n"
                "{\n"
                "    string Url()\n"
                "    {\n"
                "        return \"https://example.test//path\";\n"
                "    }\n"
                "}\n", encoding="utf-8")

            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_size_limits_and_direct_file_count(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            source = target / "Large.cs"
            body = "\n".join("        System.Console.WriteLine(1);" for _ in range(41))
            source.write_text(
                "class Large\n{\n    void Run()\n    {\n"
                + body + "\n    }\n}\n"
                + "// " + "x" * 120 + "\n"
                + "\n" * 401,
                encoding="utf-8",
            )
            for index in range(10):
                (target / f"Extra{index}.cs").write_text(
                    f"class Extra{index} {{}}\n", encoding="utf-8")

            result = self.run_cli("lint", target)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for rule in ("NK001", "NK002", "NK003", "NK011"):
                self.assertIn(rule, result.stdout)

    def test_expression_lambda_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Lambda.cs"
            path.write_text(
                "class Example\n{\n"
                "    void Run()\n    {\n"
                "        System.Func<int, int, int, int, int, int, int> combine = "
                "(a, b, c, d, e, f) => a + b + c + d + e + f;\n"
                "    }\n}\n", encoding="utf-8")

            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("NK004", result.stdout)

    def test_global_using_is_not_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "Imports.cs"
            path.write_text("global using System;\n", encoding="utf-8")

            result = self.run_cli("lint", path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_compile_items_and_symbols(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project_dir = target / "App"
            project_dir.mkdir()
            project = project_dir / "App.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk">'
                '<PropertyGroup><TargetFramework>net10.0</TargetFramework>'
                '<DefineConstants>FEATURE</DefineConstants></PropertyGroup>'
                '<ItemGroup><Compile Remove="Ignored.cs" />'
                '<Compile Include="../Shared.cs" /></ItemGroup>'
                '</Project>', encoding="utf-8")
            (project_dir / "Ignored.cs").write_text(
                "class Ignored { int first, second; }\n", encoding="utf-8")
            (project_dir / "Feature.cs").write_text(
                "#if FEATURE\nclass Feature\n{\n"
                "    int Six(int a, int b, int c, int d, int e, int f) => a;\n"
                "}\n#endif\n", encoding="utf-8")
            (target / "Shared.cs").write_text(
                "class Shared\n{\n"
                "    int Six(int a, int b, int c, int d, int e, int f) => a;\n"
                "}\n", encoding="utf-8")

            result = self.run_cli("lint", project)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("NK004"), 2, result.stdout)
            self.assertIn("Shared.cs", result.stdout)
            self.assertIn("Feature.cs", result.stdout)
            self.assertNotIn("Ignored.cs", result.stdout)
            self.assertNotIn("NK005", result.stdout)

            checked = self.run_cli("check", project)
            self.assertEqual(checked.returncode, 1,
                             checked.stdout + checked.stderr)
            self.assertIn("Shared.cs", checked.stdout)
            self.assertIn("Feature.cs", checked.stdout)
            self.assertNotIn("Ignored.cs", checked.stdout)

            created = subprocess.run(
                ["dotnet", "new", "sln", "--name", "Workspace"],
                cwd=target, capture_output=True, text=True,
            )
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            solution = target / "Workspace.slnx"
            added = subprocess.run(
                ["dotnet", "sln", str(solution), "add", str(project)],
                cwd=target, capture_output=True, text=True,
            )
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)

            solution_result = self.run_cli("lint", solution)
            self.assertEqual(solution_result.returncode, 1,
                             solution_result.stdout + solution_result.stderr)
            self.assertEqual(solution_result.stdout.count("NK004"), 2,
                             solution_result.stdout)

    def test_multi_target_project_evaluates_each_compile_group(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project = target / "Multi.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk">'
                '<PropertyGroup><TargetFrameworks>net8.0;net10.0</TargetFrameworks>'
                '<EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>'
                '<ItemGroup>'
                '<Compile Include="Eight.cs" Condition="\'$(TargetFramework)\' == \'net8.0\'" />'
                '<Compile Include="Ten.cs" Condition="\'$(TargetFramework)\' == \'net10.0\'" />'
                '<Compile Include="Shared.cs" />'
                '</ItemGroup></Project>', encoding="utf-8")
            for name in ("Eight", "Ten"):
                (target / f"{name}.cs").write_text(
                    f"class {name} {{ int first, second; }}\n", encoding="utf-8")
            (target / "Shared.cs").write_text(
                "class Shared\n{\n    int left, right;\n"
                "#if NET8_0\n"
                "    int Eight(int a, int b, int c, int d, int e, int f) => a;\n"
                "#elif NET10_0\n"
                "    int Ten(int a, int b, int c, int d, int e, int f) => a;\n"
                "#endif\n}\n", encoding="utf-8")

            result = self.run_cli("lint", project)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("NK005"), 3, result.stdout)
            self.assertEqual(result.stdout.count("NK004"), 2, result.stdout)
            self.assertEqual(result.stdout.count("Shared.cs"), 3, result.stdout)

    def test_format_and_non_destructive_check(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project = target / "Sample.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk">'
                '<PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>'
                '</Project>', encoding="utf-8")
            source = target / "Sample.cs"
            source.write_text(
                "namespace Demo; class Sample{public int Add(int left,int right)"
                "{return left+right;}}\n", encoding="utf-8")

            installed = self.run_cli("init", target)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            self.assertTrue((target / ".editorconfig").exists())

            original = source.read_bytes()
            unformatted = self.run_cli("check", project)
            self.assertNotEqual(unformatted.returncode, 0)
            self.assertEqual(source.read_bytes(), original)

            formatted = self.run_cli("format", project)
            self.assertEqual(formatted.returncode, 0, formatted.stdout + formatted.stderr)
            self.assertNotEqual(source.read_bytes(), original)

            checked = self.run_cli("check", project)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
