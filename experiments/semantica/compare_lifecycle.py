# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
"""Offline support-lifecycle study; synthetic backend inputs, no paid providers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.semantica.compare_reserved import compare as compare_reserved, make_checks
from radar_evidence.support_lifecycle import SupportWindow, evaluate_timeline
from radar_evidence.semantica_adapter import EXPECTED_SNAPSHOT, SUPPORTED_VERSION


def compare(*, semantica=False):
    raw = Path(__file__).with_name("fixtures-lifecycle.json").read_bytes()
    fixtures = json.loads(raw)
    cases = fixtures["cases"]
    if not 1 <= len(cases) <= 20 or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("invalid_fixture_cases")
    rows = []
    for case in cases:
        checks = make_checks(case)
        if len(case["windows"]) != len(checks):
            raise ValueError("invalid_fixture_windows")
        expected = case["expected_supported"]
        if (len(expected) != len(case["observations_ms"])
                or any(type(value) is not bool for value in expected)):
            raise ValueError("invalid_fixture_expectations")
        windows = [SupportWindow(check.evidence_id, **window)
                   for check, window in zip(checks, case["windows"])]
        core = evaluate_timeline(checks, windows, case["observations_ms"])
        engine = evaluate_timeline(checks, windows, case["observations_ms"],
            use_semantica=True, evaluation_budget_ms=5000) if semantica else None
        rows.append({"id": case["id"], "expected_supported": expected,
                     "core": core.to_dict(), "semantica": engine.to_dict() if engine else None,
                     "core_correct": core.evaluation_completed and
                         [f.supported for f in core.frames] == expected,
                     "matching_frames": (core.evaluation_completed and engine.evaluation_completed
                         and core.frames == engine.frames) if engine else None})
    reserved = compare_reserved()
    engine_ran = semantica and all(r["semantica"]["evaluation_completed"] for r in rows)
    return {
        "status": "STUDY_ONLY", "claim_scope": "citation_contract_only",
        "fixture_version": fixtures["fixture_version"],
        "fixture_sha256": hashlib.sha256(raw).hexdigest(),
        "ruleset_version": rows[0]["core"]["ruleset_version"],
        "lifecycle_contract": {"correct_cases": sum(r["core_correct"] for r in rows),
            "total_cases": len(rows), "total_observations": sum(len(r["expected_supported"]) for r in rows)},
        "semantica_equivalence": {"engine_ran": bool(engine_ran),
            "matching_cases": sum(r["matching_frames"] for r in rows) if engine_ran else None,
            "expected_source_snapshot": EXPECTED_SNAPSHOT,
            "expected_version": SUPPORTED_VERSION},
        "reserved_contract": reserved["citation_contract"],
        "semantic_counterexamples_still_eligible": reserved["semantic_counterexamples_still_eligible"],
        "limitations": ["Synthetic trusted backend inputs; no authentication or production homologation.",
            "All sources are required; no alternative-support or semantic entailment policy.",
            "Matching deterministic rules does not demonstrate a retrieval or legal-quality gain.",
            "No persistent watcher, database mutation, MCP server, n8n activation or paid provider."],
        "cases": rows,
    }


def gate(result, *, require_engine=False):
    contract = result["lifecycle_contract"]
    if contract["total_cases"] <= 0 or contract["correct_cases"] != contract["total_cases"]:
        return 1
    if (result["reserved_contract"] != {"correct": 13, "total": 13}
            or result["semantic_counterexamples_still_eligible"] != 4):
        return 1
    engine = result["semantica_equivalence"]
    if require_engine and not engine["engine_ran"]:
        return 2
    if require_engine and engine["matching_cases"] != contract["total_cases"]:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantica", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compare(semantica=args.semantica)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    if args.strict:
        return gate(result, require_engine=args.semantica)
    return 2 if args.semantica and not result["semantica_equivalence"]["engine_ran"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
