#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.join_lines import join_lines


def _merged_pair(total):
    n = "    int value ="
    m = "x" * (total - len(n) - 1)
    return n, m


def test_braced_array_statement_over_limit_is_kept_whole():
    code = (
        "const std::array<ScenarioEntry, 10> ScenarioCatalog::scenarios_{{\n"
        "    {'a', \"Repos (RPM = 0, servos = 0)\", scenarios::rest},\n"
        "    {'b', \"Montee (RPM > hover)\", scenarios::climb},\n"
        "    {'c', \"Descente (RPM < hover)\", scenarios::descent},\n"
        "    {'d', \"Deplacement X (hover + pitch > 0)\", scenarios::move_x},\n"
        "    {'e', \"Deplacement Y (hover + roll > 0)\", scenarios::move_y},\n"
        "    {'f', \"Combine (RPM > hover, pitch > 0, roll < 0)\", scenarios::combined},\n"
        "    {'g', \"Autonomie : altitude pure (z -> 100 m)\", flight_scenarios::autonomous_altitude},\n"
        "    {'h', \"Autonomie : axe X en cascade (x 20 -> 0)\", flight_scenarios::autonomous_position_x},\n"
        "    {'i', \"Autonomie : axe Y en cascade (y -15 -> 0)\", flight_scenarios::autonomous_position_y},\n"
        "    {'j', \"Autonomie : mission complete (TAKEOFF a COMPLETE)\", flight_scenarios::autonomous_mission},\n"
        "}};\n"
    )
    assert join_lines(code) == code


def test_braced_statement_whose_whole_join_exceeds_limit_is_kept():
    code = (
        "std::vector<std::string> labels = {\n"
        "    \"alpha beta gamma delta epsilon zeta eta theta iota kappa lambda\",\n"
        "    \"one two three four five six seven eight nine ten eleven twelve\",\n"
        '    "final entry with some extra padding to be sure OK"};\n'
    )
    assert join_lines(code) == code


def test_braced_statement_within_limit_is_joined():
    code = (
        "const std::array<int, 3> values = {\n"
        "    10,\n"
        "    20,\n"
        "    30};\n"
    )
    expected = "const std::array<int, 3> values = { 10, 20, 30};\n"
    assert join_lines(code) == expected


def test_braced_call_with_inner_braced_init_above_limit_is_kept():
    code = (
        "    run_mission(controller, aircraft,\n"
        "                {.target = {.z = 100.0}, .duration = 90.0,\n"
        "                 .axis = TrackingAxis::z_axis, .tolerance = 2.0});\n"
    )
    assert join_lines(code) == code


def test_plain_enum_after_code_is_preserved():
    code = (
        "    int value = 5;\n"
        "    enum Color {\n"
        "        RED,\n"
        "        GREEN,\n"
        "        BLUE\n"
        "    };\n"
    )
    assert join_lines(code) == code


def test_single_logical_condition_in_if_is_joined():
    code = (
        "        if (last_received >= 0.0\n"
        "            && current_time - last_received > config_.heartbeat_timeout_s) {\n"
        "            is_healthy = false;\n"
        "        }\n"
    )
    expected = (
        "        if (last_received >= 0.0 && current_time - last_received > config_.heartbeat_timeout_s) {\n"
        "            is_healthy = false;\n"
        "        }\n"
    )
    assert join_lines(code) == expected


def test_single_logical_condition_in_return_is_joined():
    code = (
        "    return last_received >= 0.0\n"
        "        && current_time - last_received > timeout;\n"
    )
    expected = "    return last_received >= 0.0 && current_time - last_received > timeout;\n"
    assert join_lines(code) == expected


def test_single_logical_or_condition_is_joined():
    code = (
        "    if (state == MissionState::COMPLETE\n"
        "        || state == MissionState::CLIMB) {\n"
        "        proceed();\n"
        "    }\n"
    )
    expected = (
        "    if (state == MissionState::COMPLETE || state == MissionState::CLIMB) {\n"
        "        proceed();\n"
        "    }\n"
    )
    assert join_lines(code) == expected
