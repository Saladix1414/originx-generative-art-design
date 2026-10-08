import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    append_promotion_decision,
    canonical_ids,
    decide_canonical_promotion,
    empty_canonical_ledger,
    evaluate_quality_gates,
)


VALID_SHA = "a" * 64


def _promotion(decision="promoted"):
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

    report = evaluate_quality_gates(
        candidate_id="candidate-0001",
        provenance_manifest=manifest,
        art_spec={"token_id": "token-0001", "rules": ["deterministic"]},
    )

    if decision == "blocked":
        report["summary"]["required_passed"] = False
        report["summary"]["failed_required"] = ["manual-block"]

    return decide_canonical_promotion(
        candidate_id="candidate-0001",
        canonical_id="canonical-0001",
        quality_report=report,
    )


def test_canonical_ledger_matches_schema():
    ledger = append_promotion_decision(
        empty_canonical_ledger(),
        _promotion(),
    )

    schema = json.loads(
        Path("schemas/ox-canonical-ledger-1.schema.json").read_text()
    )

    jsonschema.validate(ledger, schema)

    assert ledger["schema_version"] == "ox-canonical-ledger-1"
    assert ledger["entries"][0]["index"] == 0
    assert ledger["entries"][0]["decision"] == "promoted"


def test_canonical_ledger_is_append_only_by_returning_new_ledger():
    ledger = empty_canonical_ledger()
    next_ledger = append_promotion_decision(ledger, _promotion())

    assert ledger["entries"] == []
    assert len(next_ledger["entries"]) == 1


def test_canonical_ids_only_returns_promoted_entries():
    ledger = empty_canonical_ledger()
    ledger = append_promotion_decision(ledger, _promotion())
    ledger = append_promotion_decision(ledger, _promotion(decision="blocked"))

    assert canonical_ids(ledger) == ["canonical-0001"]


def test_canonical_ledger_rejects_invalid_promotion_evidence():
    promotion = _promotion()
    promotion["evidence"]["provenance_manifest_sha256"] = ""

    with pytest.raises(ValueError, match="provenance_manifest_sha256"):
        append_promotion_decision(
            empty_canonical_ledger(),
            promotion,
        )
