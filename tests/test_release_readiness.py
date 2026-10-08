import json
from pathlib import Path

import jsonschema

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    append_promotion_decision,
    build_canonical_output_manifest,
    build_review_pack,
    decide_canonical_promotion,
    empty_canonical_ledger,
    evaluate_quality_gates,
    evaluate_release_readiness,
)


def _review_pack():
    provenance = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256="b" * 64,
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

    ledger = append_promotion_decision(empty_canonical_ledger(), promotion)

    output = build_canonical_output_manifest(
        canonical_id="canonical-0001",
        candidate_id="candidate-0001",
        promotion_decision=promotion,
        provenance_manifest=provenance,
        ledger=ledger,
    )

    return build_review_pack(
        review_id="review-0001",
        provenance_manifest=provenance,
        quality_report=quality,
        promotion_decision=promotion,
        ledger=ledger,
        output_manifest=output,
    )


def test_release_readiness_matches_schema_when_ready():
    readiness = evaluate_release_readiness(
        release_id="release-0001",
        review_pack=_review_pack(),
        release_authority_granted=True,
    )

    schema = json.loads(Path("schemas/ox-release-readiness-1.schema.json").read_text())
    jsonschema.validate(readiness, schema)

    assert readiness["schema_version"] == "ox-release-readiness-1"
    assert readiness["status"] == "ready"
    assert readiness["checks"]["review_ready"] is True
    assert readiness["checks"]["schema_chain_complete"] is True
    assert readiness["checks"]["release_authority_granted"] is True


def test_release_readiness_blocks_without_authority():
    readiness = evaluate_release_readiness(
        release_id="release-0001",
        review_pack=_review_pack(),
        release_authority_granted=False,
    )

    assert readiness["status"] == "blocked"
    assert readiness["checks"]["release_authority_granted"] is False


def test_release_readiness_blocks_incomplete_schema_chain():
    review = _review_pack()
    review["documents"]["quality_schema_version"] = "wrong"

    readiness = evaluate_release_readiness(
        release_id="release-0001",
        review_pack=review,
        release_authority_granted=True,
    )

    assert readiness["status"] == "blocked"
    assert readiness["checks"]["schema_chain_complete"] is False
