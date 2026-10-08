import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.provenance import build_provenance_manifest
from oxgad.quality import (
    append_promotion_decision,
    build_canonical_output_manifest,
    decide_canonical_promotion,
    empty_canonical_ledger,
    evaluate_quality_gates,
)


VALID_SHA = "f" * 64


def _chain():
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

    promotion = decide_canonical_promotion(
        candidate_id="candidate-0001",
        canonical_id="canonical-0001",
        quality_report=report,
    )

    ledger = append_promotion_decision(
        empty_canonical_ledger(),
        promotion,
    )

    return manifest, promotion, ledger


def test_canonical_output_manifest_matches_schema():
    manifest, promotion, ledger = _chain()

    output = build_canonical_output_manifest(
        canonical_id="canonical-0001",
        candidate_id="candidate-0001",
        promotion_decision=promotion,
        provenance_manifest=manifest,
        ledger=ledger,
    )

    schema = json.loads(
        Path("schemas/ox-canonical-output-manifest-1.schema.json").read_text()
    )

    jsonschema.validate(output, schema)

    assert output["schema_version"] == "ox-canonical-output-manifest-1"
    assert output["artifact"]["sha256"] == VALID_SHA
    assert output["evidence"]["promotion_decision"] == "promoted"
    assert output["evidence"]["ledger_index"] == 0


def test_canonical_output_manifest_blocks_unpromoted_decision():
    manifest, promotion, ledger = _chain()
    promotion["decision"] = "blocked"

    with pytest.raises(ValueError, match="promoted"):
        build_canonical_output_manifest(
            canonical_id="canonical-0001",
            candidate_id="candidate-0001",
            promotion_decision=promotion,
            provenance_manifest=manifest,
            ledger=ledger,
        )


def test_canonical_output_manifest_requires_matching_ledger_entry():
    manifest, promotion, ledger = _chain()

    with pytest.raises(ValueError, match="ledger"):
        build_canonical_output_manifest(
            canonical_id="canonical-9999",
            candidate_id="candidate-0001",
            promotion_decision=promotion,
            provenance_manifest=manifest,
            ledger=ledger,
        )
