import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROJECT = ROOT / "csharp" / "NkLint.csproj"


class CliTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            ["dotnet", "build", str(PROJECT), "--nologo", "-v:q"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def run_cli(self, command, path, *options):
        return subprocess.run(
            ["dotnet", "run", "--no-build", "--project", str(PROJECT), "--", command, str(path), *options],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
