#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.return_only_var_checks import (
    check_return_only_variable,
    format_return_only_var_message,
)


def check_code(code):
    return check_return_only_variable('\n'.join(code))


def test_executable_statement_then_new_declaration_reports_only_second():
    code = [
        'auto a = 1;',
        'do_something(a);',
        'auto b = 2;',
        'return b;',
    ]
    assert check_code(code) == [(3, 'b')]


# --- Message formatting --------------------------------------------------
def test_message_text():
    assert format_return_only_var_message('validity') == (
        "Variable 'validity' déclarée uniquement pour être retournée immédiatement. "
        "Préférer un 'return' direct de l'expression."
    )


if __name__ == '__main__':
    import unittest

    _globals = globals()
    _cases = [name for name in _globals if name.startswith('test_')]

    class _Wrapper(unittest.TestCase):
        pass

    for _name in _cases:
        setattr(_Wrapper, _name, staticmethod(_globals[_name]))

    unittest.main()
