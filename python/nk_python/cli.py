"""Command line entry point for formatting and checking Python projects."""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from .ast_checks import check_source
from .comment_checks import LANGUAGE_AVAILABLE, check_comments
from .model import Issue
from .ruff_runner import run_ruff
from .structure_checks import discover


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nk-python")
    parser.add_argument("command", choices=("check", "format"), help="Check without writing, or format in place.")
    parser.add_argument(
        "paths", nargs="*", default=["."], help="Python files or directories (default: current directory)."
    )
    parser.add_argument("--max-files", type=_positive_int, default=8, help="Maximum direct Python files per directory.")
    arguments = parser.parse_args(argv)

    if importlib.util.find_spec("ruff") is None:
        print("Ruff is required. Install this tool with: pip install -e ./python", file=sys.stderr)
        return 2
    try:
        files, structure_issues = discover([Path(value) for value in arguments.paths], arguments.max_files)
    except (FileNotFoundError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    if not files:
        print("No Python files found.", file=sys.stderr)
        return 2

    if arguments.command == "format":
        import_status = run_ruff("check", files, "--select", "I", "--fix")
        format_status = run_ruff("format", files)
        return max(import_status, format_status)

    return _check(files, structure_issues)


def _check(files: list[Path], structure_issues: list[Issue]) -> int:
    lint_output: list[str] = []
    import_output: list[str] = []
    format_output: list[str] = []
    lint_status = run_ruff("check", files, "--ignore", "I", "--unfixable", "ALL", output=lint_output)
    issues = structure_issues + _check_files(files)
    import_status = run_ruff("check", files, "--select", "I", output=import_output)
    format_status = run_ruff("format", files, "--check", output=format_output)
    lint_text, import_text, format_text = ("".join(output) for output in (lint_output, import_output, format_output))
    diagnostic_pattern = r"^.+:\d+:\d+: "
    lint_count = len(re.findall(diagnostic_pattern, lint_text, re.MULTILINE)) + len(issues)
    import_count = len(re.findall(diagnostic_pattern, import_text, re.MULTILINE))
    format_count = sum(
        int(count) for count in re.findall(r"^(\d+) files? would be reformatted", format_text, re.MULTILINE)
    )
    print("=== Check summary ===")
    print(f"Files checked: {len(files)}")
    print(f"Linter: {lint_count} warnings")
    print(f"Formatter: {import_count} import diagnostics; {format_count} files to reformat")
    if 2 in (lint_status, import_status, format_status):
        print("Ruff could not complete the check; counts may be incomplete.")

    print("\n=== Linter diagnostics ===")
    print(lint_text, end="")
    for issue in sorted(issues):
        print(issue)
    if not LANGUAGE_AVAILABLE:
        print("Comment language check skipped (install nk-python-style[comments] to enable it).")

    print("\n=== Formatter: corrections available via 'format' ===")
    print(import_text, end="")
    print(format_text, end="")
    return int(bool(lint_status or import_status or format_status or issues))


def _positive_int(value: str) -> int:
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("--max-files must be positive")
    return result


def _check_files(files: list[Path]) -> list[Issue]:
    issues: list[Issue] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            issues.append(Issue(path, 1, "PY000", f"Cannot read UTF-8 source: {error}."))
            continue
        source_issues, functions = check_source(path, source)
        issues.extend(source_issues)
        issues.extend(check_comments(path, source, functions))
    return issues
