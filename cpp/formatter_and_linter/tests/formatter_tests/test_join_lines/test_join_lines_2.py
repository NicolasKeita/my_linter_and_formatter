#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_call_after_multiline_signature_is_still_joined():
    code = (
        "TiltTargets FlightController::updatePositionControl(const TargetState&   t,\n"
        "                                                    const AircraftState& a,\n"
        "                                                    double               dt)\n"
        "{\n"
        "    int result = compute(first_arg,\n"
        "                         second_arg,\n"
        "                         third_arg);\n"
        "    return TiltTargets{};\n"
        "}\n"
    )
    expected = (
        "TiltTargets FlightController::updatePositionControl(const TargetState&   t,\n"
        "                                                    const AircraftState& a,\n"
        "                                                    double               dt)\n"
        "{\n"
        "    int result = compute(first_arg, second_arg, third_arg);\n"
        "    return TiltTargets{};\n"
        "}\n"
    )
    assert join_lines(code) == expected


def test_signature_stream_and_call_together_are_handled():
    code = (
        "TiltTargets FlightController::updatePositionControl(const TargetState&   t,\n"
        "                                                    const AircraftState& a,\n"
        "                                                    double               dt)\n"
        "{\n"
        '    std::cout << "t = " << timeSeconds\n'
        "              << \"s   z = \" << state.z << std::endl;\n"
        "    int result = compute(first_arg,\n"
        "                         second_arg);\n"
        "    return TiltTargets{};\n"
        "}\n"
    )
    expected = (
        "TiltTargets FlightController::updatePositionControl(const TargetState&   t,\n"
        "                                                    const AircraftState& a,\n"
        "                                                    double               dt)\n"
        "{\n"
        '    std::cout << "t = " << timeSeconds\n'
        "              << \"s   z = \" << state.z << std::endl;\n"
        "    int result = compute(first_arg, second_arg);\n"
        "    return TiltTargets{};\n"
        "}\n"
    )
    assert join_lines(code) == expected


def test_access_specifier_does_not_swallow_next_line():
    code = (
        "class Application\n"
        "{\n"
        "public:\n"
        "    int Run() const;\n"
        "private:\n"
        "    void Helper();\n"
        "};\n"
    )
    assert join_lines(code) == code


def test_case_and_default_labels_do_not_swallow_next_line():
    code = (
        "    switch (mode) {\n"
        "    case 1:\n"
        "        do_one();\n"
        "        break;\n"
        "    default:\n"
        "        do_default();\n"
        "    }\n"
    )
    assert join_lines(code) == code


def test_braced_case_and_default_labels_do_not_swallow_next_line():
    code = (
        "    switch (mode) {\n"
        "    case FaultType::SensorFault: {\n"
        "        const std::uint64_t corruption_roll = generator() % 3;\n"
        "        scenario.sensor_corruption = static_cast<SensorCorruptionMode>(corruption_roll + 1);\n"
        "        break;\n"
        "    }\n"
        "    default: {\n"
        "        do_default();\n"
        "        break;\n"
        "    }\n"
        "    }\n"
    )
    assert join_lines(code) == code
