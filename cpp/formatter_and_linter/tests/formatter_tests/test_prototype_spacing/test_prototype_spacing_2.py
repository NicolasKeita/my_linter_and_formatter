#!/usr/bin/env python3
"""Tests split into part 2."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from formatter.spacing.prototype_spacing import clean_code

RAW_INPUT = (
    "namespace sim::test::sil {\n"
    "\n"
    "using sim::safety::FaultDomain;\n"
    "using sim::sil::FaultScenario;\n"
    "\n"
    "SimulationResult run_case(const std::vector<FaultScenario>& scenarios);\n"
    "\n"
    "\n"
    "void nominal_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records);\n"
    "\n"
    "void fc1_failure_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records);\n"
    " \n"
    "\t\n"
    "void sensor_fault_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records)\n"
    "{\n"
    "    std::cout << \"\\n=== SIL-004 ===\" << std::endl;\n"
    "\n"
    "\n"
    "    FaultDomain domain;\n"
    "\n"
    "    domain.activate();\n"
    "}\n"
    "\n"
    "}"
)

EXPECTED_OUTPUT = (
    "namespace sim::test::sil {\n"
    "\n"
    "using sim::safety::FaultDomain;\n"
    "using sim::sil::FaultScenario;\n"
    "\n"
    "SimulationResult run_case(const std::vector<FaultScenario>& scenarios);\n"
    "void nominal_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records);\n"
    "void fc1_failure_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records);\n"
    "\n"
    "void sensor_fault_scenario(TestHarness& runner, std::vector<ScenarioRecord>& records)\n"
    "{\n"
    "    std::cout << \"\\n=== SIL-004 ===\" << std::endl;\n"
    "\n"
    "\n"
    "    FaultDomain domain;\n"
    "\n"
    "    domain.activate();\n"
    "}\n"
    "\n"
    "}"
)


class TestPrototypeSpacing(unittest.TestCase):
    def test_blank_kept_between_prototype_and_using_block(self):
        code = (
            "void first(int value);\n"
            "\n"
            "using sim::sil::FaultScenario;\n"
            "\n"
            "void second(int value);\n"
        )
        self.assertEqual(clean_code(code), code)

    def test_blank_lines_inside_function_body_preserved(self):
        code = (
            "void run(int value)\n"
            "{\n"
            "    int a = 1;\n"
            "\n"
            "    int b = 2;\n"
            "\n"
            "\n"
            "    int c = 3;\n"
            "}\n"
        )
        self.assertEqual(clean_code(code), code)

    def test_comments_prototypes_and_block_comment(self):
        code = (
            "/*\n"
            "Filename: Src/Test.cpp\n"
            "*/\n"
            "\n"
            "void first(int value); // trailing comment\n"
            "\n"
            "void second(int value);\n"
        )
        expected = (
            "/*\n"
            "Filename: Src/Test.cpp\n"
            "*/\n"
            "\n"
            "void first(int value); // trailing comment\n"
            "void second(int value);\n"
        )
        self.assertEqual(clean_code(code), expected)

    def test_idempotent(self):
        self.assertEqual(clean_code(EXPECTED_OUTPUT), EXPECTED_OUTPUT)


if __name__ == "__main__":
    unittest.main()
