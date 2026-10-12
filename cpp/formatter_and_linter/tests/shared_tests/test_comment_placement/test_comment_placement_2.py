#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared.comment_utils import check_comment_placement, detect_comments_and_functions


def placement_violations(code: str):
    comments, function_lines, declaration_lines = detect_comments_and_functions(code)
    return check_comment_placement(comments, function_lines, declaration_lines)


class TestCommentPlacement(unittest.TestCase):
    def test_header_comment_in_first_lines_is_valid(self):
        code = (
            "// file header note\n"
            "\n"
            "constexpr int kFoo{1};\n"
            "\n"
            "int get_foo()\n"
            "{\n"
            "    return kFoo;\n"
            "}\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_type_declaration_is_valid(self):
        code = (
            "// scenario descriptor\n"
            "struct Scenario\n"
            "{\n"
            "    int id;\n"
            "};\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_nodiscard_function_is_valid(self):
        code = (
            "/*\n"
            "doc\n"
            "*/\n"
            "[[nodiscard]] int get_bar()\n"
            "{\n"
            "    return 1;\n"
            "}\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_template_nodiscard_function_is_valid(self):
        code = (
            "/*\n"
            "doc\n"
            "*/\n"
            "template<typename Number>\n"
            "[[nodiscard]] Number get_bar(Number n)\n"
            "{\n"
            "    return n;\n"
            "}\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_nodiscard_declaration_is_valid(self):
        code = (
            "/*\n"
            "doc\n"
            "*/\n"
            "[[nodiscard]] int get_bar();\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_nodiscard_namespace_function_is_valid(self):
        code = (
            "namespace sim::hil {\n"
            "/*\n"
            "doc\n"
            "*/\n"
            "    [[nodiscard]] int get_bar()\n"
            "    {\n"
            "        return 1;\n"
            "    }\n"
            "}\n"
        )
        self.assertEqual(placement_violations(code), [])

    def test_comment_above_nested_template_function_is_valid(self):
        code = (
            "/* Polls UART bytes until one valid protocol message is available. */\n"
            "std::expected<std::optional<Message>, TransportError> ZephyrUartInterFcTransport::poll() noexcept\n"
            "{\n"
            "    return {};\n"
            "}\n"
        )
        self.assertEqual(placement_violations(code), [])


if __name__ == "__main__":
    unittest.main()
