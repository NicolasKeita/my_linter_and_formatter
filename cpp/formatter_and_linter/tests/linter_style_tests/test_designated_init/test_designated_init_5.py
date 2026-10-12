#!/usr/bin/env python3
"""Tests split into part 5."""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.core.linter import lint_code
from linter.style.designated_init_checks import (
    check_designated_init_candidates,
)


def check_code(code):
    return check_designated_init_candidates('\n'.join(code))


# --- End-to-end integration ------------------------------------------------
def test_lint_code_flags_designated_init_warning():
    code = (
        'void run()\n'
        '{\n'
        '    TypeVariable nom_variable{};\n'
        '    nom_variable.nom_champ = valeur;\n'
        '\n'
        '}\n'
    )
    capture = io.StringIO()
    with contextlib.redirect_stderr(capture):
        has_issues = lint_code(code)
    assert has_issues
    assert '[C++20-designated-init]' in capture.getvalue()
    assert 'TypeVariable nom_variable{.nom_champ = ...};' in capture.getvalue()


def test_lint_code_is_clean_without_designated_init_pattern():
    code = (
        'void run()\n'
        '{\n'
        '    TypeVariable nom_variable{.nom_champ = valeur};\n'
        '\n'
        '}\n'
    )
    capture = io.StringIO()
    with contextlib.redirect_stderr(capture):
        has_issues = lint_code(code)
    assert not has_issues
    assert '[C++20-designated-init]' not in capture.getvalue()


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
