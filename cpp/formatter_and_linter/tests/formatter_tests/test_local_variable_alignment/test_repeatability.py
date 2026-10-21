#!/usr/bin/env python3
"""Tests split into part 5."""

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
    def test_multiline_group_is_idempotent(self):
        code = [
            "void f() {",
            "    int small = 1;",
            "    SimulationResult result{",
            "        .run_id = run_id,",
            "    };",
            "    std::array<FaultScenario, 1> scenarios{ fault };",
            "",
            "    use(small, scenarios);",
            "}",
        ]
        once = align(code)
        self.assertEqual(align(once.splitlines()), once)

    def test_control_structure_after_multiline_statement_ends_block(self):
        code = [
            "void f() {",
            "    int small = 1;",
            "    SimulationResult result{",
            "        .run_id = run_id,",
            "    };",
            "    if (small > 0) {",
            "        use(result);",
            "    }",
            "}",
        ]
        target = len("SimulationResult") + 1
        expected = [
            "void f() {",
            aligned_line("    ", "int", "small", " = 1;", target),
            aligned_line("    ", "SimulationResult", "result", "{", target),
            "        .run_id = run_id,",
            "    };",
            "    if (small > 0) {",
            "        use(result);",
            "    }",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_multiple_functions_each_aligned(self):
        code = [
            "void a() {",
            "    int x = 1;",
            "    long_name y = 2;",
            "    use(x, y);",
            "}",
            "",
            "void b() {",
            "    int q = 3;",
            "    long_name r = 4;",
            "    use(q, r);",
            "}",
        ]
        target = len("long_name") + 1
        expected = [
            "void a() {",
            aligned_line("    ", "int", "x", " = 1;", target),
            aligned_line("    ", "long_name", "y", " = 2;", target),
            "    use(x, y);",
            "}",
            "",
            "void b() {",
            aligned_line("    ", "int", "q", " = 3;", target),
            aligned_line("    ", "long_name", "r", " = 4;", target),
            "    use(q, r);",
            "}",
        ]
        self.assertEqual(align(code), "\n".join(expected) + "\n")

    def test_pass_is_idempotent(self):
        code = [
            "void generate_faults() {",
            "    std::uniform_real_distribution<std::float64_t> unit(0.0, 1.0);",
            "    const std::uint64_t fault_roll = generator() % 6;",
            "    SimulationResult result{.sil_result = sil_result, .failure_reason = FailureReason::None};",
            "",
            "    apply_fault(fault_roll);",
            "}",
        ]
        once = align(code)
        self.assertEqual(align(once.splitlines()), once)

    def test_empty_input(self):
        self.assertEqual(align_first_declaration_blocks(""), "")


if __name__ == "__main__":
    unittest.main()
