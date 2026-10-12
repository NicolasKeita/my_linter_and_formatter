#!/usr/bin/env python3
"""Tests split into part 3."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_enum_declaration_is_preserved():
    code = (
        "enum class MissionState {\n"
        "    TAKEOFF,\n"
        "    CLIMB,\n"
        "    STATION_KEEPING,\n"
        "    COMPLETE\n"
        "};\n"
    )
    assert join_lines(code) == code


def test_enum_with_underlying_type_is_preserved():
    code = (
        "enum class Axis : std::uint8_t {\n"
        "    x_axis,\n"
        "    y_axis,\n"
        "    z_axis\n"
        "};\n"
    )
    assert join_lines(code) == code


def test_enum_with_brace_on_next_line_is_preserved():
    code = (
        "enum class MissionState\n"
        "{\n"
        "    TAKEOFF,\n"
        "    CLIMB\n"
        "};\n"
    )
    assert join_lines(code) == code


def test_consecutive_attribute_prototypes_are_not_joined():
    code = (
        "[[nodiscard]] std::string format_seconds(double value);\n"
        "[[nodiscard]] std::string format_metric(double value);\n"
    )
    assert join_lines(code) == code


def test_attribute_prototype_after_function_body_is_not_joined():
    code = (
        "void helper()\n"
        "{\n"
        "    do_work();\n"
        "}\n"
        "[[nodiscard]] std::string format_metric(double value);\n"
    )
    assert join_lines(code) == code


def test_plain_consecutive_prototypes_are_not_joined():
    code = (
        "void format_seconds(double value);\n"
        "void format_metric(double value);\n"
    )
    assert join_lines(code) == code


def test_constructor_initializer_list_is_kept():
    code = (
        "SILRunner::RunContext::RunContext(const SilConfig& cfg)\n"
        "    : config{cfg},\n"
        "      fc1{cfg.controller},\n"
        "      comms{cfg.seed},\n"
        "      bus{cfg.bus}\n"
        "{\n"
        "    boot(cfg);\n"
        "}\n"
    )
    assert join_lines(code) == code


def test_constructor_initializer_list_with_multiline_signature_is_kept():
    code = (
        "SILRunner::RunContext::RunContext(const SilConfig& cfg,\n"
        "                                  std::uint32_t seed)\n"
        "    : config{cfg},\n"
        "      comms{seed}\n"
        "{\n"
        "}\n"
    )
    assert join_lines(code) == code


def test_single_member_constructor_initializer_is_kept():
    code = (
        "FlightController::FlightController(ControllerConfig config)\n"
        "    : config_(config)\n"
        "{\n"
        "    reset_pids();\n"
        "}\n"
    )
    assert join_lines(code) == code
