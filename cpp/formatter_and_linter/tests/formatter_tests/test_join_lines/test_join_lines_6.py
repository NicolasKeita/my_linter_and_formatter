#!/usr/bin/env python3
"""Tests split into part 6."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_comment_inside_string_is_not_a_comment_marker():
    code = (
        'std::string url =\n'
        '    "http://example.com/path";\n'
    )
    expected = 'std::string url = "http://example.com/path";\n'
    assert join_lines(code) == expected


def test_comment_between_wrapped_lines_blocks_joining():
    code = (
        "    int value =\n"
        "        // see below\n"
        "        42;\n"
    )
    assert join_lines(code) == code


def test_block_comment_header_is_never_joined():
    code = (
        "/*\n"
        "Filename: Src/App/Application.cpp\n"
        "Description: Application entry point.\n"
        "*/\n"
    )
    assert join_lines(code) == code


def test_preprocessor_directives_are_never_joined():
    code = (
        "constexpr int kMax =\n"
        "#if defined(_WIN32)\n"
        "    1000;\n"
        "#endif\n"
    )
    assert join_lines(code) == code


def test_include_directive_at_start_of_second_line_is_protected():
    code = (
        "    const int value =\n"
        "#include <limits>\n"
    )
    assert join_lines(code) == code


def test_function_definition_allman_brace_is_preserved():
    code = (
        "void foo()\n"
        "{\n"
        "    return;\n"
        "}\n"
    )
    assert join_lines(code) == code


def test_empty_function_body_is_preserved():
    code = (
        "void foo()\n"
        "{\n"
        "}\n"
    )
    assert join_lines(code) == code


def test_existing_single_line_control_brace_keeps_its_body():
    code = (
        "    if (cond) {\n"
        "        do_something();\n"
        "    }\n"
    )
    assert join_lines(code) == code


def test_standalone_control_brace_is_joined_to_header():
    code = (
        "    if (condition)\n"
        "    {\n"
        "        return x;\n"
        "    }\n"
    )
    expected = (
        "    if (condition) {\n"
        "        return x;\n"
        "    }\n"
    )
    assert join_lines(code) == expected


def test_lambda_body_is_not_swallowed():
    code = (
        "    auto scale = [](double input) {\n"
        "        return input * 2.0;\n"
        "    };\n"
    )
    assert join_lines(code) == code
