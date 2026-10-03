"""Métricas top-1 e abstenção, sem alterar recuperação ou reserva."""
import hashlib
import json
from pathlib import Path

from avaliar import carregar, medir


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def retrieval_metrics(rows):
    """Citação errada conta FP e FN; abstenção só é correta sem suporte.

    Precision@1 usa todas as citações emitidas. Recall@1 usa todas as perguntas
    com documento esperado. São métricas de recuperação, não de texto gerado.
    """
    correct = sum(r["obtido"] is not None and r["obtido"] == r["esperado"] for r in rows)
    emitted = sum(r["obtido"] is not None for r in rows)
    answerable = sum(r["esperado"] is not None for r in rows)
    abstained = len(rows) - emitted
    unsupported = len(rows) - answerable
    correct_abstentions = sum(r["obtido"] is None and r["esperado"] is None for r in rows)
    false_citations_without_support = sum(r["obtido"] is not None and r["esperado"] is None for r in rows)
    return {
        "total": len(rows), "correct_citations": correct, "emitted_citations": emitted,
        "answerable": answerable, "abstained": abstained, "unsupported": unsupported,
        "correct_abstentions": correct_abstentions,
        "precision_at_1": ratio(correct, emitted), "recall_at_1": ratio(correct, answerable),
        "abstention_precision": ratio(correct_abstentions, abstained),
        "abstention_recall": ratio(correct_abstentions, unsupported),
        "unsupported_false_positive_rate": ratio(false_citations_without_support, unsupported),
        "wrong_citations": emitted - correct,
    }


def report():
    datasets = {}
    for filename in ("desenvolvimento.json", "reserva.json"):
        raw = (Path(__file__).parent / "dados" / filename).read_bytes()
        cases = carregar(filename)
        datasets[filename] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "methods": {name: retrieval_metrics(medir(cases, expandir=expanded)["casos"])
                        for name, expanded in (("literal", False), ("equivalencias", True))},
        }
    return {"scope": "synthetic_top_1_retrieval_only", "datasets": datasets,
            "limits": ["No generated answer, entailment or legal correctness is evaluated.",
                       "Four reserved cases do not establish statistical generalization.",
                       "None denotes an undefined metric denominator, never a perfect score."]}


if __name__ == "__main__":
    print(json.dumps(report(), ensure_ascii=False, sort_keys=True, indent=2))
