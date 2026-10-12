#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.multiple_var_decl_checks import MULTIPLE_VAR_DECL_MESSAGE, check_multiple_var_declarations


def check_code(code: str):
    return check_multiple_var_declarations('\n'.join(code))


class TestMultipleVarDeclarations(unittest.TestCase):
    def test_preprocessor_lines_are_ignored(self):
        code = [
            '#define PAIR(a, b) a, b',
        ]
        self.assertEqual(check_code(code), [])

    def test_message_text(self):
        self.assertEqual(MULTIPLE_VAR_DECL_MESSAGE, "[MULTIPLE_VAR_DECL] Declare only one variable per line.")


if __name__ == "__main__":
    unittest.main()
