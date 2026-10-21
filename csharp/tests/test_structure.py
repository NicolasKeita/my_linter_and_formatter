import pathlib
import tempfile

from _cli_support import CliTestCase


class StructureTests(CliTestCase):
    def test_direct_subdirectory_limit_for_directories_and_projects(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            source = target / "Sample.cs"
            source.write_text("class Sample {}\n", encoding="utf-8")
            project = target / "Sample.csproj"
            project.write_text(
                '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                "<TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>",
                encoding="utf-8",
            )
            for index in range(8):
                (target / f"Part{index}" / "Nested").mkdir(parents=True)
            for ignored in (".git", ".vs", "bin", "obj", "node_modules", "TestResults"):
                for index in range(9):
                    (target / ignored / str(index)).mkdir(parents=True)
            for count in (8, 9):
                if count == 9:
                    (target / "Part8").mkdir()
                for path in (target, project):
                    with self.subTest(count=count, path=path):
                        result = self.run_cli("lint", path)
                        self.assertEqual(result.returncode, int(count > 8), result.stdout + result.stderr)
                        if count > 8:
                            self.assertEqual(result.stdout.count("NK012"), 1)
                            self.assertIn("9 sous-dossiers directs (maximum : 8)", result.stdout)
            single = self.run_cli("lint", source)
            self.assertEqual(single.returncode, 0, single.stdout + single.stderr)

    def test_nested_subdirectory_limit_without_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            nested = target / "Nested"
            for index in range(9):
                (nested / str(index)).mkdir(parents=True)
            result = self.run_cli("lint", target)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("NK012"), 1)
            self.assertIn("Nested", result.stdout)
