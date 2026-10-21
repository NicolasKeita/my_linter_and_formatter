import pathlib
import tempfile

from _cli_support import CliTestCase
from _project_fixtures import create_format_project


class FormattingTests(CliTestCase):
    def test_format_and_non_destructive_check(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            project, source = create_format_project(target)
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
