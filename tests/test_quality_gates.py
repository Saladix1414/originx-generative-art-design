import json
from pathlib import Path

import jsonschema

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import evaluate_quality_gates


VALID_SHA = "c" * 64


def _manifest():
    return build_provenance_manifest(
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


def test_quality_gate_report_matches_schema():
    report = evaluate_quality_gates(
        candidate_id="candidate-0001",
        provenance_manifest=_manifest(),
        art_spec={
            "token_id": "token-0001",
            "rules": ["local-first", "deterministic"],
        },
    )

    schema = json.loads(
        Path("schemas/ox-quality-gate-report-1.schema.json").read_text()
    )

    jsonschema.validate(report, schema)

    assert report["schema_version"] == "ox-quality-gate-report-1"
    assert report["summary"]["passed"] is True
    assert report["summary"]["failed_required"] == []


def test_quality_gate_report_fails_missing_required_evidence():
    manifest = _manifest()
    manifest["integrity"]["manifest_sha256"] = ""

    report = evaluate_quality_gates(
        candidate_id="",
        provenance_manifest=manifest,
        art_spec={},
    )

    assert report["summary"]["passed"] is False
    assert "candidate-id-present" in report["summary"]["failed_required"]
    assert "provenance-integrity-present" in report["summary"]["failed_required"]
    assert "art-spec-identity-present" in report["summary"]["failed_required"]


def test_quality_gate_advisory_failure_does_not_block_required_pass():
    report = evaluate_quality_gates(
        candidate_id="candidate-0001",
        provenance_manifest=_manifest(),
        art_spec={
            "token_id": "token-0001",
        },
    )

    assert report["summary"]["required_passed"] is True
    assert report["summary"]["passed"] is True
    assert report["summary"]["failed_required"] == []
    assert report["summary"]["failed_advisory"] == ["art-spec-has-rules"]
