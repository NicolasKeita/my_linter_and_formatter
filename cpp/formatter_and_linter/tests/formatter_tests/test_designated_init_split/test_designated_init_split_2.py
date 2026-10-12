#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.designated_init_split_formatter import split_long_designated_initializations


def _long_scenario_line():
    return (
        "    const FaultScenario                         scenario{"
        ".start_time = 30.0, .fault_type = FaultType::CommunicationLoss, "
        ".duration_s = 10.0, .is_critical = true};\n"
    )


def _expected_scenario_block():
    return (
        "    const FaultScenario                         scenario{\n"
        "                                                    .start_time = 30.0,\n"
        "                                                    .fault_type = FaultType::CommunicationLoss,\n"
        "                                                    .duration_s = 10.0,\n"
        "                                                    .is_critical = true,\n"
        "                                                };\n"
    )


def _short_config_line():
    return (
        "    const SilConfig                             config{"
        ".duration_s = 32.0, .trace_level = SilLogLevel::Trace};\n"
    )


def test_designated_with_brace_value_is_split():
    code = (
        "    const MissionConfig mission{.target{.z = 100.0}, .duration = 120.0, "
        ".axis = TrackingAxis::x_axis, .tolerance = 0.5, .enabled = true, .name = \"x\"};\n"
    )
    assert len(code.rstrip()) > 120
    result = split_long_designated_initializations(code)
    assert "                            .target{.z = 100.0},\n" in result


def test_class_and_enum_declarations_are_untouched():
    values = "FirstValue = 1, SecondValue = 2, ThirdValue = 3, FourthValue = 4, FifthValue = 5, SixthValue = 6"
    prefix = "    enum class VeryLongEnumNameForTestingTheBehaviour{"
    code = prefix + values + "};\n"
    assert len(code.rstrip()) > 120
    assert split_long_designated_initializations(code) == code


def test_strings_and_chars_are_protected_from_splitting():
    code = (
        "    const LabelConfig label{.text = \"a, b\", .sep = ',', .x = 1, .y = 2, .z = 3, "
        ".w = 4, .h = 5, .size = 6, .bold = true};\n"
    )
    assert len(code.rstrip()) > 120
    result = split_long_designated_initializations(code)
    assert '.text = "a, b",' in result
    assert ".sep = ',',\n" in result


def test_pass_is_idempotent():
    once = split_long_designated_initializations(_long_scenario_line())
    twice = split_long_designated_initializations(once)
    assert twice == once


def test_empty_code_is_returned_unchanged():
    assert split_long_designated_initializations("") == ""
