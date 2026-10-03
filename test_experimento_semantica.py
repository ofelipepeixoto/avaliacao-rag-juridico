# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
"""Evaluation-specific regression gates; independent of the library repository."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

class ExperimentGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parent / "experiments/semantica/compare_reserved.py"
        spec = importlib.util.spec_from_file_location("radar_compare_reserved_tests", source)
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def gate(self, *, correct=13, matching=11, engine_ran=True, real=False):
        fixture_result = {"citation_contract": {"correct": correct, "total": 13},
            "semantica_equivalence": {"engine_ran": engine_ran,
                "matching_verdicts": matching, "valid_input_cases": 11}}
        arguments = ["compare_reserved.py", "--strict"] + (["--semantica"] if real else [])
        with patch.object(self.runner, "compare", return_value=fixture_result), \
             patch.object(sys, "argv", arguments), contextlib.redirect_stdout(io.StringIO()):
            return self.runner.main()

    def test_strict_core_regression_fails(self):
        self.assertEqual(self.gate(correct=12), 1)

    def test_strict_equivalence_regression_fails(self):
        self.assertEqual(self.gate(matching=10, real=True), 1)

    def test_missing_real_engine_has_distinct_exit_code(self):
        self.assertEqual(self.gate(engine_ran=False, matching=None, real=True), 2)

    def test_known_contract_and_equivalence_pass(self):
        self.assertEqual(self.gate(real=True), 0)

    def test_verified_modules_do_not_count_as_completed_engine_evaluation(self):
        from radar_evidence.semantica_adapter import SupportEvaluation
        for reason in ("evaluation_budget_exceeded", "engine_contract_mismatch", "engine_error"):
            with self.subTest(reason=reason):
                failure = SupportEvaluation(False, (reason,), engine_version="0.7.0",
                    verified_modules=("verified",) * 10)
                with patch.object(self.runner, "evaluate_support", return_value=failure):
                    result = self.runner.compare(semantica=True)
                self.assertFalse(result["semantica_equivalence"]["engine_ran"])
                self.assertIsNone(result["semantica_equivalence"]["matching_verdicts"])

    def test_core_only_report_does_not_claim_an_engine_run(self):
        result = self.runner.compare()
        self.assertFalse(result["semantica_equivalence"]["engine_ran"])
        self.assertEqual(result["citation_contract"], {"correct": 13, "total": 13})


if __name__ == "__main__":
    unittest.main()
