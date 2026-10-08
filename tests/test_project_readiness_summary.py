import json
from pathlib import Path

import jsonschema

from oxgad.quality import summarize_project_readiness


def _review(ready=True):
    return {
        "schema_version": "ox-review-pack-1",
        "project": "originx-generative-art-design",
        "phase": "phase13",
        "review_id": "review-0001",
        "canonical_id": "canonical-0001",
        "candidate_id": "candidate-0001",
        "documents": {
            "provenance_schema_version": "ox-provenance-manifest-1",
            "quality_schema_version": "ox-quality-gate-report-1",
            "promotion_schema_version": "ox-canonical-promotion-1",
            "ledger_schema_version": "ox-canonical-ledger-1",
            "output_manifest_schema_version": "ox-canonical-output-manifest-1",
        },
        "summary": {
            "ready_for_review": ready,
            "promotion_decision": "promoted",
            "quality_required_passed": ready,
            "ledger_index": 0,
        },
    }


def _release(status="ready"):
    return {
        "schema_version": "ox-release-readiness-1",
        "project": "originx-generative-art-design",
        "phase": "phase14",
        "release_id": "release-0001",
        "review_id": "review-0001",
        "canonical_id": "canonical-0001",
        "status": status,
        "checks": {
            "review_ready": status == "ready",
            "schema_chain_complete": status == "ready",
            "release_authority_granted": status == "ready",
        },
    }


def _release_ledger(record=True):
    return {
        "schema_version": "ox-release-ledger-1",
        "project": "originx-generative-art-design",
        "phase": "phase15",
        "entries": [
            {
                "index": 0,
                "release_id": "release-0001",
                "review_id": "review-0001",
                "canonical_id": "canonical-0001",
                "status": "ready",
                "release_schema_version": "ox-release-readiness-1",
            }
        ] if record else [],
    }


def _export_audit(record=True):
    return {
        "schema_version": "ox-export-audit-ledger-1",
        "project": "originx-generative-art-design",
        "phase": "phase19",
        "entries": [
            {
                "index": 0,
                "export_id": "export-0001",
                "status": "exported",
                "manifest_path": "output/canonical/canonical-0001/manifest.json",
                "artifact_path": "output/canonical/canonical-0001/artifact.png",
                "export_result_schema_version": "ox-local-export-result-1",
            }
        ] if record else [],
    }


def test_project_readiness_summary_matches_schema_when_ready():
    summary = summarize_project_readiness(
        review_pack=_review(),
        release_readiness=_release(),
        release_ledger=_release_ledger(),
        export_audit_ledger=_export_audit(),
    )

    schema = json.loads(
        Path("schemas/ox-project-readiness-summary-1.schema.json").read_text()
    )
    jsonschema.validate(summary, schema)

    assert summary["schema_version"] == "ox-project-readiness-summary-1"
    assert summary["status"] == "ready"
    assert all(summary["checks"].values())


def test_project_readiness_blocks_missing_export_record():
    summary = summarize_project_readiness(
        review_pack=_review(),
        release_readiness=_release(),
        release_ledger=_release_ledger(),
        export_audit_ledger=_export_audit(record=False),
    )

    assert summary["status"] == "blocked"
    assert summary["checks"]["export_recorded"] is False


def test_project_readiness_blocks_missing_release_record():
    summary = summarize_project_readiness(
        review_pack=_review(),
        release_readiness=_release(),
        release_ledger=_release_ledger(record=False),
        export_audit_ledger=_export_audit(),
    )

    assert summary["status"] == "blocked"
    assert summary["checks"]["release_recorded"] is False
