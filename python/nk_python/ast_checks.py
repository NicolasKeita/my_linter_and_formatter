"""Checks that need Python syntax rather than regular expressions."""

import ast
from pathlib import Path

from .model import Issue

MAX_LINE_LENGTH = 120
MAX_FILE_LINES = 120
MAX_FUNCTION_LINES = 40
MAX_PARAMETERS = 5


def function_ranges(tree: ast.AST, source: str) -> list[tuple[int, int]]:
    lines = source.splitlines()
    ranges = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = node.end_lineno or node.lineno
        for index in range(end, len(lines)):
            stripped = lines[index].lstrip(" \t")
            if not stripped:
                continue
            indentation = len(lines[index]) - len(stripped)
            if stripped.startswith("#") and indentation > node.col_offset:
                end = index + 1
                continue
            break
        ranges.append((node.lineno, end))
    return ranges


def check_source(path: Path, source: str) -> tuple[list[Issue], list[tuple[int, int]]]:
    issues: list[Issue] = []
    lines = source.splitlines()
    for number, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_LENGTH:
            issues.append(Issue(path, number, "PY001", f"Line has {len(line)} characters (max {MAX_LINE_LENGTH})."))
    if len(lines) > MAX_FILE_LINES:
        issues.append(Issue(path, MAX_FILE_LINES + 1, "PY002", f"File has {len(lines)} lines (max {MAX_FILE_LINES})."))

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        issues.append(Issue(path, error.lineno or 1, "PY000", f"Invalid Python syntax: {error.msg}."))
        return issues, []

    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        length = (node.end_lineno or node.lineno) - node.lineno + 1
        if length > MAX_FUNCTION_LINES:
            issues.append(
                Issue(
                    path, node.lineno, "PY003", f"Function '{node.name}' has {length} lines (max {MAX_FUNCTION_LINES})."
                )
            )
        count = _parameter_count(node, parents.get(node))
        if count > MAX_PARAMETERS:
            issues.append(
                Issue(
                    path, node.lineno, "PY004", f"Function '{node.name}' has {count} parameters (max {MAX_PARAMETERS})."
                )
            )
    return issues, function_ranges(tree, source)


def _parameter_count(node: ast.FunctionDef | ast.AsyncFunctionDef, parent: ast.AST | None) -> int:
    positional = node.args.posonlyargs + node.args.args
    count = len(positional) + len(node.args.kwonlyargs)
    count += int(node.args.vararg is not None) + int(node.args.kwarg is not None)
    is_static = any(
        isinstance(decorator, ast.Name) and decorator.id == "staticmethod" for decorator in node.decorator_list
    )
    if isinstance(parent, ast.ClassDef) and not is_static and positional and positional[0].arg in {"self", "cls"}:
        count -= 1
    return count
