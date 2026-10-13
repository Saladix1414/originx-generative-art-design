import json
from pathlib import Path

import jsonschema

from oxgad.models.model_acceptance_gate import (
    build_model_acceptance_gate,
    model_acceptance_passed,
)
from oxgad.models.sd15_operational_status import (
    load_sd15_operational_status,
    validate_sd15_operational_status,
)


def test_sd15_is_authoritatively_rejected():
    value = load_sd15_operational_status()
    validate_sd15_operational_status(value)

    assert value["modelId"] == "OX-MODEL-002"
    assert value["status"] == "REJECTED_FOR_PRODUCTION"
    assert value["technicalGate"] == "FAIL"
    assert value["visualGate"] == "FAIL"
    assert value["rejectionReason"] == (
        "DOMINANT_BANDING_ARTIFACT"
    )
    assert value["role"] is None
    assert value["productionAlias"] is None
    assert value["productionAliasState"] == {
        "alias": "OX-GENESIS-MODEL-1",
        "state": "UNASSIGNED",
    }


def test_rejection_blocks_all_generation_actions():
    governance = load_sd15_operational_status()["governance"]

    assert all(flag is False for flag in governance.values())


def test_rejection_evidence_preserves_three_attempts():
    status = load_sd15_operational_status()
    evidence = json.loads(
        Path(status["evidence"]["reference"]).read_text()
    )

    assert len(
        evidence["controlledComparison"]["attempts"]
    ) == 3
    assert evidence["assessment"]["qualityScore"] == 0
    assert (
        evidence["assessment"][
            "vaeAsPrincipalDemonstratedCause"
        ]
        is False
    )
    assert evidence["preservation"]["deletionAllowed"] is False


def test_model_acceptance_gate_matches_schema():
    value = build_model_acceptance_gate()
    schema = json.loads(
        Path(
            "schemas/ox-model-acceptance-gate-1.schema.json"
        ).read_text()
    )
    jsonschema.validate(value, schema)

    assert value["invariant"] == (
        "ONE_STEP_PREFLIGHT != PRODUCTION_VALIDATION"
    )


def test_one_step_preflight_cannot_promote_model():
    assert model_acceptance_passed(
        hardware_preflight=True,
        minimal_inference_preflight=True,
        full_representative_generation=False,
        image_integrity_inspection=False,
        visual_quality_gate=False,
    ) is False


def test_all_acceptance_stages_are_required():
    assert model_acceptance_passed(
        hardware_preflight=True,
        minimal_inference_preflight=True,
        full_representative_generation=True,
        image_integrity_inspection=True,
        visual_quality_gate=True,
    ) is True
