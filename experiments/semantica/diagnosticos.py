"""Separar elegibilidade do contrato e anotações de suporte semântico."""
import json
from compare_reserved import compare


def diagnostics(result):
    rows = result["cases"]
    positive = [r for r in rows if r["expected_contract_supported"]]
    negative = [r for r in rows if not r["expected_contract_supported"]]
    accepted = [r for r in rows if r["core_supported"]]
    false_positive = sum(r["core_supported"] for r in negative)
    false_negative = sum(not r["core_supported"] for r in positive)
    semantic_counterexamples = sum(r["semantic_counterexample_annotation"] for r in accepted)
    return {"scope": "synthetic_citation_contract_only",
            "fixture_sha256": result["fixture_sha256"],
            "contract": {"positive_cases": len(positive), "negative_cases": len(negative),
                         "false_positives": false_positive, "false_negatives": false_negative,
                         "precision": (len(accepted)-false_positive)/len(accepted) if accepted else None,
                         "recall": (len(positive)-false_negative)/len(positive) if positive else None},
            "semantic_support_limitation": {
                "eligible_citations": len(accepted),
                "eligible_counterexamples_annotated_unsupported": semantic_counterexamples,
                "counterexample_share_of_eligible": semantic_counterexamples/len(accepted) if accepted else None,
                "generated_answers_evaluated": 0},
            "limits": ["Contract eligibility does not test entailment or authenticate identity.",
                       "Security inputs are trusted synthetic fixtures; these counts are not attack coverage.",
                       "Semantic labels are annotations; no LLM or semantic judge ran."]}


if __name__ == "__main__":
    print(json.dumps(diagnostics(compare()), ensure_ascii=False, sort_keys=True, indent=2))
