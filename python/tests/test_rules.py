import tempfile
import unittest
from pathlib import Path

from nk_python.ast_checks import check_source
from nk_python.comment_checks import LANGUAGE_AVAILABLE, check_comments
from nk_python.structure_checks import discover


def codes(source: str) -> set[str]:
    path = Path("sample.py")
    issues, functions = check_source(path, source)
    issues.extend(check_comments(path, source, functions))
    return {issue.code for issue in issues}


class RuleTests(unittest.TestCase):
    def test_function_and_parameter_limits_exclude_method_receiver(self):
        source = "class Box:\n    def read(self, a, b, c, d, e):\n        return a\n"
        self.assertNotIn("PY004", codes(source))
        source += "\n    async def write(self, a, b, c, d, e, f):\n        return a\n"
        self.assertIn("PY004", codes(source))

    def test_function_length_and_file_length(self):
        source = "def large():\n" + "    pass\n" * 40
        self.assertIn("PY003", codes(source))
        self.assertNotIn("PY002", codes(source))
        self.assertIn("PY002", codes("x = 1\n" * 121))
        self.assertIn("PY001", codes("x = '" + "x" * 121 + "'\n"))

    def test_comments_do_not_confuse_strings_docstrings_or_directives(self):
        source = (
            "def item():\n"
            '    """A # symbol in a docstring."""\n'
            "    text = '# not a comment'\n"
            "    value = 1  # type: ignore[assignment]\n"
            "    # explain the unusual branch\n"
            "    return value\n"
        )
        self.assertIn("PY006", codes(source))
        self.assertNotIn("PY005", codes(source))
        self.assertNotIn("PY007", codes(source.replace("# explain the unusual branch", "# a short note")))

    def test_inline_comment_and_language(self):
        self.assertIn("PY005", codes("value = 1  # a comment next to code\n"))
        if LANGUAGE_AVAILABLE:
            self.assertIn("PY007", codes("# Cette fonction calcule la valeur finale pour chaque entrée.\nvalue = 1\n"))
            self.assertNotIn("PY007", codes("# This function computes the final value for every input.\nvalue = 1\n"))

    def test_trailing_comment_stays_in_function_scope(self):
        source = "def item():\n    return 1\n    # trailing inside function\n# outside function\n"
        path = Path("sample.py")
        _, functions = check_source(path, source)
        comments = check_comments(path, source, functions)
        self.assertEqual([(issue.line, issue.code) for issue in comments if issue.code == "PY006"], [(3, "PY006")])

    def test_structure_counts_direct_sources_and_ignores_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for number in range(9):
                (root / f"file_{number}.py").write_text("x = 1\n", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "ignored.py").write_text("", encoding="utf-8")
            files, issues = discover([root], max_files=8)
            self.assertEqual(len(files), 9)
            self.assertEqual([issue.code for issue in issues], ["PY008"])


if __name__ == "__main__":
    unittest.main()
