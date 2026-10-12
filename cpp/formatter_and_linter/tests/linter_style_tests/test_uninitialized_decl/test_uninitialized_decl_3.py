#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.uninitialized_decl_checks import (
    check_uninitialized_declarations,
    format_uninitialized_decl_message,
)


def check_code(code):
    return check_uninitialized_declarations('\n'.join(code))


class TestUninitializedDeclarations(unittest.TestCase):
    def test_template_type_declaration_is_reported(self):
        code = [
            'std::map<std::uint32_t, std::string> lookup;',
            'lookup.index = 1;',
        ]
        self.assertEqual(check_code(code), [(1, 'lookup')])

    def test_nested_template_type_declaration_is_reported(self):
        code = [
            'std::map<std::string, std::vector<int>> values;',
            'values.count = 1;',
        ]
        self.assertEqual(check_code(code), [(1, 'values')])

    def test_reference_declaration_is_reported(self):
        code = [
            'Config& config;',
            'config.count = 1;',
        ]
        self.assertEqual(check_code(code), [(1, 'config')])

    def test_multiple_declarators_are_not_reported(self):
        code = [
            'Type a, b;',
            'a.champ = 1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_two_statements_on_one_line_are_not_reported(self):
        code = [
            'TypeVar ma_var; prepare();',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_string_content_is_ignored(self):
        code = [
            'TypeVar ma_var;',
            'log("ma_var.champ1 = val1");',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_message_text(self):
        self.assertEqual(
            format_uninitialized_decl_message('injected'),
            "Variable 'injected' déclarée puis initialisée par assignation membre par membre. "
            "Préférer l'initialisation directe ou un designated initializer (C++20).",
        )


if __name__ == '__main__':
    unittest.main()
