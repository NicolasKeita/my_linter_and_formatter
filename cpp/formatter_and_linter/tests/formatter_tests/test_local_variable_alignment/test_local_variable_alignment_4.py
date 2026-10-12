#!/usr/bin/env python3
"""Tests split into part 4."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.declarations.local_variable_alignment_formatter import align_first_declaration_blocks


def align(code):
    return align_first_declaration_blocks("\n".join(code) + "\n")


def aligned_line(indent, type_part, name, rest, target):
    return indent + type_part + " " * (target - len(type_part)) + name + rest


class TestLocalVariableAlignment(unittest.TestCase):
    MULTILINE_BRACE_INIT_CODE = [
        "void MonteCarloRunner::execute_run(std::uint64_t run_id)",
        "{",
        "    Scenario            scenario = generator_.generate_scenario(run_id);",
        "    const SilConfig     config = make_run_config(config_, scenario);",
        "    const FaultScenario fault = scenario.to_fault_scenario();",
        "    const bool          fault_expected = (scenario.fault_type != FaultType::None);",
        "    SimulationResult             result{",
        "                                     .run_id = run_id,",
        "                                     .scenario_seed = scenario.scenario_seed,",
        "                                     .scenario = scenario,",
        "                                 };",
        "    SILRunner                    runner(config);",
        "    std::array<FaultScenario, 1> scenarios{ fault };",
        "    auto                         outcome = runner.run(std::span<const FaultScenario>{ scenarios });",
        "",
        "    execute(runner, scenarios);",
        "}",
    ]

    def test_multiline_brace_init_stays_in_same_group(self):
        target = len("std::array<FaultScenario, 1>") + 1
        expected = [
            "void MonteCarloRunner::execute_run(std::uint64_t run_id)",
            "{",
            aligned_line("    ", "Scenario", "scenario", " = generator_.generate_scenario(run_id);", target),
            aligned_line("    ", "const SilConfig", "config", " = make_run_config(config_, scenario);", target),
            aligned_line("    ", "const FaultScenario", "fault", " = scenario.to_fault_scenario();", target),
            aligned_line(
                "    ",
                "const bool",
                "fault_expected",
                " = (scenario.fault_type != FaultType::None);",
                target,
            ),
            "    SimulationResult             result{",
            "                                     .run_id = run_id,",
            "                                     .scenario_seed = scenario.scenario_seed,",
            "                                     .scenario = scenario,",
            "                                 };",
            aligned_line("    ", "SILRunner", "runner", "(config);", target),
            aligned_line("    ", "std::array<FaultScenario, 1>", "scenarios", "{ fault };", target),
            aligned_line(
                "    ",
                "auto",
                "outcome",
                " = runner.run(std::span<const FaultScenario>{ scenarios });",
                target,
            ),
            "",
            "    execute(runner, scenarios);",
            "}",
        ]
        self.assertEqual(align(self.MULTILINE_BRACE_INIT_CODE), "\n".join(expected) + "\n")

    def test_multiline_brace_init_column_is_uniform(self):
        code = [
            "void f() {",
            "    int small = 1;",
            "    SimulationResult result{",
            "        .run_id = run_id,",
            "        .scenario = scenario,",
            "    };",
            "    std::array<FaultScenario, 1> scenarios{ fault };",
            "}",
        ]
        result = align(code).splitlines()
        columns = {
            result[1].index("small"),
            result[2].index("result"),
            result[6].index("scenarios"),
        }
        self.assertEqual(len(columns), 1)

    def test_multiline_paren_init_stays_in_same_group(self):
        code = [
            "void f() {",
            "    int small = 1;",
            "    SILRunner runner(",
            "        config,",
            "        telemetry);",
            "    long_name other = 2;",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "void f() {",
            aligned_line("    ", "int", "small", " = 1;", target),
            "    SILRunner runner(",
            "        config,",
            "        telemetry);",
            aligned_line("    ", "long_name", "other", " = 2;", target),
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")


if __name__ == "__main__":
    unittest.main()
