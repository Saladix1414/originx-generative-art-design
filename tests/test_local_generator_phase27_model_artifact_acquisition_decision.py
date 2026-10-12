import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_decision import (
    MODEL_ARTIFACT_ACQUISITION_DECISION_VERSION,
    build_blocked_model_artifact_acquisition_decision,
    model_artifact_acquisition_decision_hash,
    validate_model_artifact_acquisition_decision,
)
from oxgad.models.artifact_evidence import build_missing_model_artifact_evidence


def test_model_artifact_acquisition_decision_is_schema_valid_and_blocked():
    decision = build_blocked_model_artifact_acquisition_decision()
    schema = json.loads(
        Path(
            "schemas/ox-model-artifact-acquisition-decision-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(decision, schema)
    validate_model_artifact_acquisition_decision(decision)

    assert decision["decisionVersion"] == (
        MODEL_ARTIFACT_ACQUISITION_DECISION_VERSION
    )
    assert decision["decision"] == "BLOCKED_NO_ARTIFACT"
    assert decision["source"]["artifactEvidenceState"] == "MISSING"
    assert decision["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "decisionGrantsAcquisitionAuthority": False,
        "decisionGrantsExecutionAuthority": False,
    }


def test_model_artifact_acquisition_decision_hash_is_deterministic():
    first = build_blocked_model_artifact_acquisition_decision()
    second = build_blocked_model_artifact_acquisition_decision()

    assert first == second
    assert first["modelArtifactAcquisitionDecisionHash"] == (
        model_artifact_acquisition_decision_hash(first)
    )


def test_model_artifact_acquisition_decision_rejects_trusted_evidence():
    evidence = build_missing_model_artifact_evidence()
    evidence["governance"]["evidenceGrantsTrust"] = True

    with pytest.raises(ValueError, match="trust"):
        build_blocked_model_artifact_acquisition_decision(evidence)


def test_model_artifact_acquisition_decision_rejects_hash_tampering():
    decision = build_blocked_model_artifact_acquisition_decision()
    decision["modelArtifactAcquisitionDecisionHash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_acquisition_decision(decision)


def test_model_artifact_acquisition_decision_rejects_download_authority():
    decision = build_blocked_model_artifact_acquisition_decision()
    decision["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_acquisition_decision(decision)
