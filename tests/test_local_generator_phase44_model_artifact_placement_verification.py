import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_placement_verification import (
    MODEL_ARTIFACT_PLACEMENT_VERIFICATION_VERSION,
    build_missing_model_artifact_placement_verification,
    model_artifact_placement_verification_hash,
    validate_model_artifact_placement_verification,
)


def test_model_artifact_placement_verification_is_schema_valid_and_missing():
    verification = build_missing_model_artifact_placement_verification()
    schema = json.loads(
        Path(
            "schemas/ox-model-artifact-placement-verification-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(verification, schema)
    validate_model_artifact_placement_verification(verification)

    assert verification["verificationVersion"] == (
        MODEL_ARTIFACT_PLACEMENT_VERIFICATION_VERSION
    )
    assert verification["state"] == "MISSING"
    assert verification["target"]["path"] == (
        "models/v1-5-pruned-emaonly.safetensors"
    )
    assert verification["observed"] == {
        "pathExists": False,
        "isFile": False,
        "sizeBytes": None,
    }


def test_model_artifact_placement_verification_blocks_authority():
    verification = build_missing_model_artifact_placement_verification()

    assert verification["governance"] == {
        "verificationGrantsTrust": False,
        "verificationGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }


def test_model_artifact_placement_verification_hash_is_deterministic():
    first = build_missing_model_artifact_placement_verification()
    second = build_missing_model_artifact_placement_verification()

    assert first == second
    assert first["modelArtifactPlacementVerificationHash"] == (
        model_artifact_placement_verification_hash(first)
    )


def test_model_artifact_placement_verification_rejects_execution_authority():
    verification = build_missing_model_artifact_placement_verification()
    verification["governance"]["executionAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_placement_verification(verification)


def test_model_artifact_placement_verification_rejects_hash_tampering():
    verification = build_missing_model_artifact_placement_verification()
    verification["modelArtifactPlacementVerificationHash"] = (
        "sha256:" + "0" * 64
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_placement_verification(verification)
