import pathlib
import tempfile

from _cli_support import CliTestCase
from _project_fixtures import create_feature_project, create_solution


class ProjectTests(CliTestCase):
    def test_project_compile_items_and_symbols(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project = create_feature_project(target)
            result = self.run_cli("lint", project)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("NK004"), 2, result.stdout)
            self.assertIn("Shared.cs", result.stdout)
            self.assertIn("Feature.cs", result.stdout)
            self.assertNotIn("Ignored.cs", result.stdout)
            self.assertNotIn("NK005", result.stdout)
            checked = self.run_cli("check", project)
            self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
            self.assertIn("Shared.cs", checked.stdout)
            self.assertIn("Feature.cs", checked.stdout)
            self.assertNotIn("Ignored.cs", checked.stdout)
            solution = create_solution(self, target, project)
            solution_result = self.run_cli("lint", solution)
            self.assertEqual(solution_result.returncode, 1, solution_result.stdout + solution_result.stderr)
            self.assertEqual(solution_result.stdout.count("NK004"), 2, solution_result.stdout)

    def test_multi_target_project_evaluates_each_compile_group(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project = target / "Multi.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                "<TargetFrameworks>net8.0;net10.0</TargetFrameworks>"
                "<EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>"
                "<ItemGroup><Compile Include=\"Eight.cs\" Condition=\"'$(TargetFramework)' == 'net8.0'\" />"
                "<Compile Include=\"Ten.cs\" Condition=\"'$(TargetFramework)' == 'net10.0'\" />"
                '<Compile Include="Shared.cs" /></ItemGroup></Project>',
                encoding="utf-8",
            )
            for name in ("Eight", "Ten"):
                (target / f"{name}.cs").write_text(f"class {name} {{ int first, second; }}\n", encoding="utf-8")
            (target / "Shared.cs").write_text(
                "class Shared\n"
                "{\n"
                "    int left, right;\n"
                "#if NET8_0\n"
                "    int Eight(int a, int b, int c, int d, int e, int f) => a;\n"
                "#elif NET10_0\n"
                "    int Ten(int a, int b, int c, int d, int e, int f) => a;\n"
                "#endif\n"
                "}\n",
                encoding="utf-8",
            )
            result = self.run_cli("lint", project)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("NK005"), 3, result.stdout)
            self.assertEqual(result.stdout.count("NK004"), 2, result.stdout)
            self.assertEqual(result.stdout.count("Shared.cs"), 3, result.stdout)
