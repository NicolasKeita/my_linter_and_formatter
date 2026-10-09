"""Command line entry point for formatting and checking Python projects."""

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from .ast_checks import check_source
from .comment_checks import LANGUAGE_AVAILABLE, check_comments
from .model import Issue
from .structure_checks import discover

RUFF_CONFIG = Path(__file__).with_name("ruff.toml")


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
        import_status = _run_ruff("check", files, "--select", "I", "--fix")
        format_status = _run_ruff("format", files)
        return max(import_status, format_status)

    lint_status = _run_ruff("check", files)
    format_status = _run_ruff("format", files, "--check")
    issues = structure_issues + _check_files(files)
    for issue in sorted(issues):
        print(issue)
    if not LANGUAGE_AVAILABLE:
        print("Comment language check skipped (install nk-python-style[comments] to enable it).", file=sys.stderr)
    return int(bool(lint_status or format_status or issues))


def _positive_int(value: str) -> int:
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("--max-files must be positive")
    return result


def _run_ruff(command: str, files: list[Path], *options: str) -> int:
    status = 0
    for offset in range(0, len(files), 50):
        batch = files[offset : offset + 50]
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                command,
                "--config",
                str(RUFF_CONFIG),
                *options,
                *(os.path.relpath(path) for path in batch),
            ],
            check=False,
        )
        status = max(status, result.returncode)
    return status


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
