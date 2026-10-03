# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
"""Compare unchanged lexical baseline and citation contracts on synthetic data.

No model, remote call or answer generation. Claims are annotation-only and never
feed rules/checks. A valid citation can coexist with an unsupported answer claim;
the report exposes that limitation rather than claiming semantic verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages/radar-evidence-kit/src"))

from avaliar import carregar, medir, recuperar
from radar_evidence.checks import check_evidence
from radar_evidence.modelos import Evidence, Scope
from radar_evidence.semantica_adapter import evaluate_support


def make_checks(case):
    revisions = {item["document_id"]: item.get("current_revision", 1)
                 for item in case["evidences"] if item.get("known_document", True)}
    scope = Scope("tenant-ficticio", "projeto-ficticio", revisions)
    checks = []
    for item in case["evidences"]:
        text = item["text"]
        record = {
            "tenant_id": item.get("tenant_id", "tenant-ficticio"),
            "project_id": "projeto-ficticio", "document_id": item["document_id"],
            "revision": item.get("revision", 1), "page": 1,
            "start": 0, "end": item.get("end", len(text)), "text": text,
            "source_sha256": hashlib.sha256(("synthetic-source:" + item["document_id"]).encode()).hexdigest(),
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "review_status": item.get("review_status", "approved"),
            "reviewer": "revisor-ficticio", "identity_verified": item.get("identity_verified", True),
        }
        if "extra_metadata" in item:
            record["extra_metadata"] = item["extra_metadata"]
        checks.append(check_evidence(Evidence.from_dict(record), scope))
    return checks


def compare(*, semantica=False):
    fixture_path = Path(__file__).with_name("fixtures-reservadas.json")
    raw_fixture = fixture_path.read_bytes()
    fixtures = json.loads(raw_fixture)
    rows = []
    for case in fixtures["cases"]:
        try:
            checks = make_checks(case)
            core_supported = all(check.supported for check in checks)
            core_reasons = sorted({reason for check in checks for reason in check.reasons})
            engine_input_valid = True
        except (TypeError, ValueError):
            checks = None
            core_supported = False
            core_reasons = ["input_rejected"]
            engine_input_valid = False
        engine = evaluate_support(checks, evaluation_budget_ms=5000).to_dict() if semantica else None
        rows.append({
            "id": case["id"], "category": case["category"], "question": case["question"],
            "claim_annotation_only": case["claim"],
            "lexical_literal_id": recuperar(case["question"]),
            "lexical_equivalences_id": recuperar(case["question"], expandir=True),
            "expected_contract_supported": case["expected_contract_supported"],
            "core_supported": core_supported, "core_reasons": core_reasons,
            "core_contract_correct": core_supported == case["expected_contract_supported"],
            "semantica": engine, "engine_input_valid": engine_input_valid,
            "semantic_counterexample_annotation": case["semantic_counterexample"],
        })
    baseline = {}
    for dataset in ("desenvolvimento.json", "reserva.json"):
        baseline[dataset] = {
            "literal": medir(carregar(dataset), expandir=False),
            "equivalences": medir(carregar(dataset), expandir=True),
        }
    valid_engine_rows = [row for row in rows if row["engine_input_valid"]]
    engine_ran = semantica and all(row["semantica"]["engine_version"] == "0.7.0"
        and len(row["semantica"]["verified_modules"]) == 10 for row in valid_engine_rows)
    agreement = sum(row["semantica"]["supported"] == row["core_supported"]
                    for row in valid_engine_rows) if engine_ran else None
    return {
        "fixture_version": fixtures["fixture_version"],
        "fixture_sha256": hashlib.sha256(raw_fixture).hexdigest(),
        "claim_scope": "citation_contract_only",
        "limitations": ["No entailment, legal quality, authentication or retrieval improvement is measured.",
            "Review/identity/scope are synthetic trusted inputs, not verified identities.",
            "Claims do not feed the adapter. Counterexamples deliberately remain citation-eligible."],
        "baseline_original": baseline,
        "citation_contract": {"correct": sum(row["core_contract_correct"] for row in rows),
                              "total": len(rows)},
        "semantica_equivalence": {"engine_ran": bool(engine_ran), "matching_verdicts": agreement,
                                  "valid_input_cases": len(valid_engine_rows)},
        "semantic_counterexamples_still_eligible": sum(row["core_supported"]
            and row["semantic_counterexample_annotation"] for row in rows),
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantica", action="store_true", help="Use the optional pinned real engine")
    parser.add_argument("--strict", action="store_true", help="Fail if citation contract or engine equivalence regresses")
    parser.add_argument("--output", type=Path, help="Write report JSON to this local file")
    arguments = parser.parse_args()
    result = compare(semantica=arguments.semantica)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    if arguments.semantica and not result["semantica_equivalence"]["engine_ran"]:
        return 2
    if arguments.strict:
        contract = result["citation_contract"]
        if contract["correct"] != contract["total"]:
            return 1
        engine = result["semantica_equivalence"]
        if arguments.semantica and engine["matching_verdicts"] != engine["valid_input_cases"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
