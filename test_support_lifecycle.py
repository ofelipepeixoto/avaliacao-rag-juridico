# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
import copy
import unittest
from unittest.mock import patch

from experiments.semantica import compare_lifecycle as runner
from radar_evidence.support_lifecycle import LifecycleEvaluation


class LifecycleConsumerTests(unittest.TestCase):
    def setUp(self):
        self.result = runner.compare()

    def test_synthetic_core_contracts_offline_and_four_counterexamples_preserved(self):
        with patch("socket.socket", side_effect=AssertionError("network")):
            result = runner.compare()
        self.assertEqual(runner.gate(result), 0)
        self.assertEqual(result["lifecycle_contract"], {
            "correct_cases": 10, "total_cases": 10, "total_observations": 35})
        self.assertEqual(result["semantic_counterexamples_still_eligible"], 4)
        self.assertFalse(result["semantica_equivalence"]["engine_ran"])

    def test_no_engine_is_distinct_from_successful_negative_verdict(self):
        self.assertEqual(runner.gate(self.result, require_engine=True), 2)

    def test_strict_gate_rejects_regression_and_vacuous_success(self):
        for correct, total in ((9, 10), (0, 0)):
            value = copy.deepcopy(self.result)
            value["lifecycle_contract"].update(correct_cases=correct, total_cases=total)
            self.assertEqual(runner.gate(value), 1)

    def test_strict_gate_keeps_semantic_limit_visible(self):
        self.result["semantic_counterexamples_still_eligible"] = 0
        self.assertEqual(runner.gate(self.result), 1)

    def test_strict_gate_requires_full_frame_equivalence(self):
        self.result["semantica_equivalence"].update(engine_ran=True, matching_cases=9)
        self.assertEqual(runner.gate(self.result, require_engine=True), 1)
        self.result["semantica_equivalence"]["matching_cases"] = 10
        self.assertEqual(runner.gate(self.result, require_engine=True), 0)

    def test_failed_evaluation_is_not_counted_as_matching_negative(self):
        original = runner.evaluate_timeline
        def evaluate(*args, **kwargs):
            if kwargs.get("use_semantica"):
                return LifecycleEvaluation(reasons=("engine_error",), engine="semantica")
            return original(*args, **kwargs)
        with patch.object(runner, "evaluate_timeline", side_effect=evaluate):
            result = runner.compare(semantica=True)
        self.assertFalse(result["semantica_equivalence"]["engine_ran"])
        self.assertIsNone(result["semantica_equivalence"]["matching_cases"])
        self.assertEqual(runner.gate(result, require_engine=True), 2)


if __name__ == "__main__":
    unittest.main()
