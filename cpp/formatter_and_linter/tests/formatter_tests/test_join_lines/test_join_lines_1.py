#!/usr/bin/env python3
"""Tests split into part 1."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_assignment_broken_after_equal_is_joined():
    code = (
        "    const double total =\n"
        "        value * 2.0;\n"
    )
    expected = "    const double total = value * 2.0;\n"
    assert join_lines(code) == expected


def test_function_arguments_broken_after_comma_are_joined():
    code = (
        "    int result = compute(first_arg,\n"
        "                         second_arg,\n"
        "                         third_arg);\n"
    )
    expected = "    int result = compute(first_arg, second_arg, third_arg);\n"
    assert join_lines(code) == expected


def test_multiline_call_is_joined_by_multi_pass():
    code = (
        "auto verdict = check(value > 0,\n"
        "                    value < 100,\n"
        "                    extra_condition);\n"
    )
    assert join_lines(code) == "auto verdict = check(value > 0, value < 100, extra_condition);\n"


def test_operator_at_start_of_next_line_is_joined():
    code = (
        "    int total = a\n"
        "        + b\n"
        "        - c;\n"
    )
    assert join_lines(code) == "    int total = a + b - c;\n"


def test_stream_output_continuation_is_not_joined():
    code = (
        '    std::cout << "value: "\n'
        "              << value << std::endl;\n"
    )
    assert join_lines(code) == code


def test_stream_output_with_trailing_operator_is_not_joined():
    code = (
        '    std::cout << "t = " << timeSeconds <<\n'
        '              "s   z = " << state.z << std::endl;\n'
    )
    assert join_lines(code) == code


def test_stream_output_block_stays_split():
    code = (
        '    std::cout << "t = " << std::fixed << std::setprecision(kTimePrecision) << timeSeconds\n'
        '              << "s   z = " << std::setprecision(kValuePrecision) << state.z\n'
        '              << "m/s   pitch = " << pitchDegrees\n'
        '              << "deg   rpm = " << state.actual_rpm << std::endl;\n'
    )
    assert join_lines(code) == code


def test_multiline_function_signature_params_are_kept():
    code = (
        "TiltTargets FlightController::updatePositionControl(const TargetState&   t,\n"
        "                                                    const AircraftState& a,\n"
        "                                                    double               dt)\n"
        "{\n"
        "    return TiltTargets{};\n"
        "}\n"
    )
    assert join_lines(code) == code


def test_multiline_prototype_params_are_kept():
    code = (
        "    void compute(const Config&        cfg,\n"
        "                  std::vector<double>& out);\n"
    )
    assert join_lines(code) == code
