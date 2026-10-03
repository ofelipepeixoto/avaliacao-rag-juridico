# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
"""Synthetic offline receipt; leaves no database or checkpoint on disk."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from radar_evidence import Evidence, Scope, Checkpoint, Journal, check_evidence, export_prov


def run():
    text = "Cláusula fictícia: o valor mensal é R$ 250,00."
    evidence = Evidence(
        tenant_id="operador-ficticio", project_id="contrato-demo", document_id="documento-demo",
        revision=1, page=1, start=0, end=len(text), text=text,
        source_sha256=hashlib.sha256(b"synthetic-original-demo").hexdigest(),
        text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        review_status="approved", reviewer="rotulo-ficticio", identity_verified=False,
    )
    scope = Scope(evidence.tenant_id, evidence.project_id, {evidence.document_id: 1})
    check = check_evidence(evidence, scope)
    with TemporaryDirectory() as directory:
        journal = Journal(Path(directory) / "recibos.sqlite3", scope)
        checkpoint = journal.append(evidence, check, event_id="demo-001",
            occurred_at="2026-10-03T12:00:00Z", expected_checkpoint=Checkpoint.empty(scope))
        journal.verify(checkpoint)
        return {"fixture": "synthetic-only", "check": check.to_dict(),
                "checkpoint": checkpoint.to_dict(), "prov": export_prov(journal, checkpoint),
                "checkpoint_custody": "temporary_demo_only; retain independently in an application"}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
