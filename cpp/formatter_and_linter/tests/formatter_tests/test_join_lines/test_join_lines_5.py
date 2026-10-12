#!/usr/bin/env python3
"""Tests split into part 5."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_single_condition_trailing_operator_is_joined():
    code = (
        "    if (a &&\n"
        "        b) {\n"
        "        handle();\n"
        "    }\n"
    )
    expected = (
        "    if (a && b) {\n"
        "        handle();\n"
        "    }\n"
    )
    assert join_lines(code) == expected


def test_multiple_logical_conditions_stay_split():
    code = (
        "    return std::abs(t.z - a.z) <= config_.altitude_tolerance_m\n"
        "        && std::abs(t.x - a.x) <= config_.position_tolerance_m\n"
        "        && std::abs(t.y - a.y) <= config_.position_tolerance_m;\n"
    )
    assert join_lines(code) == code


def test_multiple_logical_conditions_in_if_stay_split():
    code = (
        "        if (altitude_error < kMaxError\n"
        "            && speed_error < kMaxSpeed\n"
        "            && turn_rate < kMaxTurn) {\n"
        "            proceed();\n"
        "        }\n"
    )
    assert join_lines(code) == code


def test_multiple_logical_conditions_after_equal_stay_split():
    code = (
        "    bool healthy =\n"
        "        voltage > kMinVolt\n"
        "        && current < kMaxCurrent\n"
        "        && temperature < kMaxTemp;\n"
    )
    assert join_lines(code) == code


def test_multi_condition_trailing_operator_stays_split():
    code = (
        "    if (a &&\n"
        "        b &&\n"
        "        c) {\n"
        "        handle();\n"
        "    }\n"
    )
    assert join_lines(code) == code


def test_merged_line_of_119_columns_is_merged():
    n, m = _merged_pair(119)
    code = f"{n}\n    {m}\n"
    out = join_lines(code)
    assert out.splitlines() == [n + " " + m]
    assert len(out.splitlines()[0]) == 119


def test_merged_line_of_exactly_max_length_is_merged():
    n, m = _merged_pair(120)
    code = f"{n}\n    {m}\n"
    out = join_lines(code)
    lines = out.splitlines()
    assert len(lines) == 1
    assert len(lines[0]) == 120


def test_joined_line_of_121_columns_stays_split():
    n, m = _merged_pair(121)
    code = f"{n}\n    {m}\n"
    assert join_lines(code) == code
    assert len(code.splitlines()[0]) == 15


def test_custom_max_length_overrides_default():
    n = "int value ="
    m = "x" * 83 + ";"
    code = f"{n}\n    {m}\n"
    assert len(n) + 1 + len(m) == 96
    assert join_lines(code, max_length=95) == code
    assert join_lines(code) == n + " " + m + "\n"


def test_lines_with_line_comments_are_never_joined():
    code = (
        "    int value =\n"
        "        42; // computed at runtime\n"
    )
    assert join_lines(code) == code
