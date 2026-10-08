import json
from pathlib import Path

import jsonschema

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    decide_canonical_promotion,
    evaluate_quality_gates,
)


VALID_SHA = "e" * 64


def _quality_report():
    manifest = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256=VALID_SHA,
        created_at="2026-10-08T18:00:00+00:00",
    )

    return evaluate_quality_gates(
        candidate_id="candidate-0001",
        provenance_manifest=manifest,
        art_spec={
            "token_id": "token-0001",
            "rules": ["deterministic"],
        },
    )


def test_canonical_promotion_matches_schema_when_promoted():
    decision = decide_canonical_promotion(
        candidate_id="candidate-0001",
        canonical_id="canonical-0001",
        quality_report=_quality_report(),
    )

    schema = json.loads(
        Path("schemas/ox-canonical-promotion-1.schema.json").read_text()
    )

    jsonschema.validate(decision, schema)

    assert decision["schema_version"] == "ox-canonical-promotion-1"
    assert decision["decision"] == "promoted"
    assert decision["evidence"]["quality_required_passed"] is True
    assert decision["evidence"]["failed_required"] == []


def test_canonical_promotion_blocks_failed_quality_report():
    report = _quality_report()
    report["summary"]["required_passed"] = False
    report["summary"]["failed_required"] = ["output-hash-present"]

    decision = decide_canonical_promotion(
        candidate_id="candidate-0001",
        canonical_id="canonical-0001",
        quality_report=report,
    )

    assert decision["decision"] == "blocked"
    assert decision["evidence"]["quality_required_passed"] is False
    assert decision["evidence"]["failed_required"] == ["output-hash-present"]


def test_canonical_promotion_blocks_missing_identifiers_and_provenance():
    report = _quality_report()
    report["provenance_manifest_sha256"] = ""

    decision = decide_canonical_promotion(
        candidate_id="",
        canonical_id="",
        quality_report=report,
    )

    assert decision["decision"] == "blocked"
    assert "provenance-manifest-sha256-invalid" in decision["evidence"]["failed_required"]
    assert "promotion-identifiers-missing" in decision["evidence"]["failed_required"]
