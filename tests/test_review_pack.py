import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    append_promotion_decision,
    build_canonical_output_manifest,
    build_review_pack,
    decide_canonical_promotion,
    empty_canonical_ledger,
    evaluate_quality_gates,
)


def _chain():
    provenance = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256="a" * 64,
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

    return provenance, quality, promotion, ledger, output


def test_review_pack_matches_schema():
    provenance, quality, promotion, ledger, output = _chain()

    pack = build_review_pack(
        review_id="review-0001",
        provenance_manifest=provenance,
        quality_report=quality,
        promotion_decision=promotion,
        ledger=ledger,
        output_manifest=output,
    )

    schema = json.loads(Path("schemas/ox-review-pack-1.schema.json").read_text())
    jsonschema.validate(pack, schema)

    assert pack["schema_version"] == "ox-review-pack-1"
    assert pack["summary"]["ready_for_review"] is True
    assert pack["summary"]["ledger_index"] == 0


def test_review_pack_blocks_missing_ledger_entry():
    provenance, quality, promotion, ledger, output = _chain()
    ledger["entries"] = []

    with pytest.raises(ValueError, match="ledger"):
        build_review_pack(
            review_id="review-0001",
            provenance_manifest=provenance,
            quality_report=quality,
            promotion_decision=promotion,
            ledger=ledger,
            output_manifest=output,
        )


def test_review_pack_marks_blocked_quality_not_ready():
    provenance, quality, promotion, ledger, output = _chain()
    quality["summary"]["required_passed"] = False

    pack = build_review_pack(
        review_id="review-0001",
        provenance_manifest=provenance,
        quality_report=quality,
        promotion_decision=promotion,
        ledger=ledger,
        output_manifest=output,
    )

    assert pack["summary"]["ready_for_review"] is False
