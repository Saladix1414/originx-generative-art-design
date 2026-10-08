import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    append_promotion_decision,
    append_release_readiness,
    build_canonical_output_manifest,
    build_review_pack,
    decide_canonical_promotion,
    empty_canonical_ledger,
    empty_release_ledger,
    evaluate_quality_gates,
    evaluate_release_readiness,
    ready_release_ids,
)


def _readiness(authority=True):
    provenance = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256="c" * 64,
        created_at="2026-10-08T18:00:00+00:00",
    )

    quality = evaluate_quality_gates(
        candidate_id="candidate-0001",
        provenance_manifest=provenance,
        art_spec={"token_id": "token-0001", "rules": ["deterministic"]},
    )

    promotion = decide_canonical_promotion(
        candidate_id="candidate-0001",
        canonical_id="canonical-0001",
        quality_report=quality,
    )

    canonical_ledger = append_promotion_decision(
        empty_canonical_ledger(),
        promotion,
    )

    output = build_canonical_output_manifest(
        canonical_id="canonical-0001",
        candidate_id="candidate-0001",
        promotion_decision=promotion,
        provenance_manifest=provenance,
        ledger=canonical_ledger,
    )

    review = build_review_pack(
        review_id="review-0001",
        provenance_manifest=provenance,
        quality_report=quality,
        promotion_decision=promotion,
        ledger=canonical_ledger,
        output_manifest=output,
    )

    return evaluate_release_readiness(
        release_id="release-0001",
        review_pack=review,
        release_authority_granted=authority,
    )


def test_release_ledger_matches_schema():
    ledger = append_release_readiness(
        empty_release_ledger(),
        _readiness(),
    )

    schema = json.loads(Path("schemas/ox-release-ledger-1.schema.json").read_text())
    jsonschema.validate(ledger, schema)

    assert ledger["schema_version"] == "ox-release-ledger-1"
    assert ledger["entries"][0]["index"] == 0
    assert ledger["entries"][0]["status"] == "ready"


def test_release_ledger_is_append_only_by_returning_new_ledger():
    ledger = empty_release_ledger()
    next_ledger = append_release_readiness(ledger, _readiness())

    assert ledger["entries"] == []
    assert len(next_ledger["entries"]) == 1


def test_ready_release_ids_only_returns_ready_entries():
    ledger = empty_release_ledger()
    ledger = append_release_readiness(ledger, _readiness(authority=True))
    ledger = append_release_readiness(ledger, _readiness(authority=False))

    assert ready_release_ids(ledger) == ["release-0001"]


def test_release_ledger_rejects_invalid_schema_version():
    readiness = _readiness()
    readiness["schema_version"] = "wrong"

    with pytest.raises(ValueError, match="schema version"):
        append_release_readiness(empty_release_ledger(), readiness)
