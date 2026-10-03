import unittest

from metricas import report, retrieval_metrics


class MetricsTests(unittest.TestCase):
    def test_wrong_document_is_false_positive_and_missed_expected_citation(self):
        result = retrieval_metrics([{"esperado": "a", "obtido": "b"}])
        self.assertEqual(result["precision_at_1"], 0)
        self.assertEqual(result["recall_at_1"], 0)
        self.assertEqual(result["wrong_citations"], 1)

    def test_zero_denominators_are_not_perfect_scores(self):
        result = retrieval_metrics([])
        for key in ("precision_at_1", "recall_at_1", "abstention_precision", "abstention_recall"):
            self.assertIsNone(result[key])

    def test_reserve_keeps_false_positive_and_abstention_visible(self):
        methods = report()["datasets"]["reserva.json"]["methods"]
        for method in methods.values():
            self.assertEqual(method["precision_at_1"], 0.5)
            self.assertEqual(method["recall_at_1"], 0.5)
            self.assertEqual(method["unsupported_false_positive_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
