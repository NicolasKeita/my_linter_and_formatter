#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from linter.style.uninitialized_decl_checks import (
    check_uninitialized_declarations,
)


def check_code(code):
    return check_uninitialized_declarations('\n'.join(code))


class TestUninitializedDeclarations(unittest.TestCase):
    def test_simple_declaration_then_member_assignment_is_reported(self):
        code = [
            'TypeVar ma_var;',
            'ma_var.champ1 = val1;',
            'ma_var.champ2 = val2;',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 1)
        self.assertEqual(violations[0][1], 'ma_var')

    def test_blank_lines_and_comments_are_ignored(self):
        code = [
            'SilEvent injected;',
            '',
            '// Initialisation du contexte',
            'injected.timestamp = ctx.time;',
            'injected.source = "ENV";',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 1)
        self.assertEqual(violations[0][1], 'injected')

    def test_block_comment_is_ignored(self):
        code = [
            'SilEvent injected;',
            '/* Initialization of the context',
            '   spans several lines */',
            'injected.timestamp = ctx.time;',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 1)
        self.assertEqual(violations[0][1], 'injected')

    def test_trailing_comment_on_declaration_is_ignored(self):
        code = [
            'TypeVar ma_var; // the variable under test',
            'ma_var.champ1 = val1;',
        ]
        violations = check_code(code)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0][0], 1)

    def test_interleaved_executable_code_cancels_detection(self):
        code = [
            'TypeVar ma_var;',
            'do_something();',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_assignment_to_other_variable_cancels_detection(self):
        code = [
            'TypeVar ma_var;',
            'other.champ1 = val1;',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_comparison_cancels_detection(self):
        code = [
            'TypeVar ma_var;',
            'ma_var.champ1 == val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_compound_assignment_cancels_detection(self):
        code = [
            'TypeVar ma_var;',
            'ma_var.champ1 += val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_direct_brace_initialization_is_not_reported(self):
        code = [
            'TypeVar ma_var{};',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])

    def test_designated_initializer_is_not_reported(self):
        code = [
            'TypeVar ma_var{.champ1 = val1};',
            'ma_var.champ2 = val2;',
        ]
        self.assertEqual(check_code(code), [])

    def test_copy_initialization_is_not_reported(self):
        code = [
            'TypeVar ma_var = make_var();',
            'ma_var.champ1 = val1;',
        ]
        self.assertEqual(check_code(code), [])


if __name__ == '__main__':
    unittest.main()
