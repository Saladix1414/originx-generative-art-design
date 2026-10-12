import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_evidence import (
    MODEL_ARTIFACT_EVIDENCE_VERSION,
    build_missing_model_artifact_evidence,
    model_artifact_evidence_hash,
    validate_model_artifact_evidence,
)


def test_missing_model_artifact_evidence_is_schema_valid():
    evidence = build_missing_model_artifact_evidence()
    schema = json.loads(
        Path("schemas/ox-model-artifact-evidence-1.schema.json").read_text()
    )

    jsonschema.validate(evidence, schema)
    validate_model_artifact_evidence(evidence)

    assert evidence["evidenceVersion"] == MODEL_ARTIFACT_EVIDENCE_VERSION
    assert evidence["state"] == "MISSING"
    assert evidence["modelId"] == "originx.sd15.emaonly"
    assert evidence["observedArtifact"] == {
        "path": None,
        "format": None,
        "sha256": None,
        "sizeBytes": None,
    }


def test_missing_model_artifact_evidence_blocks_trust_and_execution():
    evidence = build_missing_model_artifact_evidence()

    assert evidence["checks"] == {
        "artifactPresent": False,
        "formatMatches": False,
        "hashMatches": False,
        "sizeMatches": False,
    }
    assert evidence["governance"] == {
        "evidenceGrantsTrust": False,
        "evidenceGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }


def test_model_artifact_evidence_hash_is_deterministic():
    first = build_missing_model_artifact_evidence()
    second = build_missing_model_artifact_evidence()

    assert first == second
    assert first["modelArtifactEvidenceHash"] == (
        model_artifact_evidence_hash(first)
    )


def test_model_artifact_evidence_rejects_hash_tampering():
    evidence = build_missing_model_artifact_evidence()
    evidence["modelArtifactEvidenceHash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_evidence(evidence)


def test_model_artifact_evidence_rejects_execution_authority():
    evidence = build_missing_model_artifact_evidence()
    evidence["governance"]["executionAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_evidence(evidence)
