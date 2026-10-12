#!/usr/bin/env python3
"""Tests split into part 7."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_else_header_does_not_swallow_its_body():
    code = (
        "    } else {\n"
        "        other();\n"
        "    }\n"
    )
    assert join_lines(code) == code


def test_braced_initializer_list_is_joined():
    code = (
        "std::vector<std::string> names = {\n"
        '    "alice",\n'
        '    "bob",\n'
        '    "carol"};\n'
    )
    expected = 'std::vector<std::string> names = { "alice", "bob", "carol"};\n'
    assert join_lines(code) == expected


def test_designated_initializer_multiline_is_joined():
    code = (
        "    const FaultScenario scenario{\n"
        "        .start_time = 20.0,\n"
        "        .duration = 10.0,\n"
        "        .fault_type = FaultType::SensorFault};\n"
    )
    expected = (
        "    const FaultScenario scenario{ .start_time = 20.0, .duration = 10.0, "
        ".fault_type = FaultType::SensorFault};\n"
    )
    assert join_lines(code) == expected


def test_wrapped_call_above_limit_stays_split():
    code = (
        "    const MissionRunTrace trace =\n"
        "        run_mission(controller, aircraft,\n"
        "                    {.target = {.z = 100.0}, .duration = 90.0,\n"
        "                     .axis = TrackingAxis::z_axis, .tolerance = 2.0});\n"
    )
    assert join_lines(code) == code


def test_semicolon_only_on_next_line_is_joined():
    code = (
        "    int value = compute(a)\n"
        "        ;\n"
    )
    expected = "    int value = compute(a) ;\n"
    assert join_lines(code) == expected


def test_trailing_newline_is_preserved():
    assert join_lines("int a =\n    1;\n") == "int a = 1;\n"
    assert join_lines("int a =\n    1;") == "int a = 1;"
    assert join_lines("int a = 1;") == "int a = 1;"


def test_empty_or_blank_input_is_left_untouched():
    assert join_lines("") == ""
    assert join_lines("\n") == "\n"
    assert join_lines("   \n") == "   \n"


def test_join_lines_is_idempotent():
    source = (
        "    const double total = value * 2.0;\n"
        "    if (condition) {\n"
        "        return x;\n"
        "    }\n"
    )
    assert join_lines(join_lines(source)) == join_lines(source)
