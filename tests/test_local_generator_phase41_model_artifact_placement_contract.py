import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_placement import (
    MODEL_ARTIFACT_PLACEMENT_VERSION,
    build_unplaced_model_artifact_placement,
    model_artifact_placement_hash,
    validate_model_artifact_placement,
)


def test_model_artifact_placement_is_schema_valid_and_unplaced():
    placement = build_unplaced_model_artifact_placement()
    schema = json.loads(
        Path("schemas/ox-model-artifact-placement-1.schema.json").read_text()
    )

    jsonschema.validate(placement, schema)
    validate_model_artifact_placement(placement)

    assert placement["placementVersion"] == MODEL_ARTIFACT_PLACEMENT_VERSION
    assert placement["state"] == "UNPLACED"
    assert placement["target"] == {
        "directory": "models",
        "filename": "v1-5-pruned-emaonly.safetensors",
        "path": "models/v1-5-pruned-emaonly.safetensors",
    }
    assert placement["observed"] == {
        "pathExists": False,
        "hashObserved": False,
        "sizeObserved": False,
    }


def test_model_artifact_placement_blocks_trust_execution_and_generation():
    placement = build_unplaced_model_artifact_placement()

    assert placement["governance"] == {
        "placementGrantsTrust": False,
        "placementGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }


def test_model_artifact_placement_hash_is_deterministic():
    first = build_unplaced_model_artifact_placement()
    second = build_unplaced_model_artifact_placement()

    assert first == second
    assert first["modelArtifactPlacementHash"] == (
        model_artifact_placement_hash(first)
    )


def test_model_artifact_placement_rejects_execution_authority():
    placement = build_unplaced_model_artifact_placement()
    placement["governance"]["executionAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_placement(placement)


def test_model_artifact_placement_rejects_hash_tampering():
    placement = build_unplaced_model_artifact_placement()
    placement["modelArtifactPlacementHash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_placement(placement)
