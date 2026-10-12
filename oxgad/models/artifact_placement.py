"""Model artifact placement declaration for local generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.acquisition import build_first_local_model_plan

MODEL_ARTIFACT_PLACEMENT_VERSION = "OX-MODEL-ARTIFACT-PLACEMENT-1"
_SCHEMA_PATH = Path("schemas/ox-model-artifact-placement-1.schema.json")
_TARGET_PATH = Path("models/v1-5-pruned-emaonly.safetensors")


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_placement_hash(
    placement: Mapping[str, Any],
) -> str:
    payload = dict(placement)
    payload.pop("modelArtifactPlacementHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_unplaced_model_artifact_placement() -> dict[str, Any]:
    """Declare where the first local model artifact must be placed."""
    plan = build_first_local_model_plan()

    placement = {
        "placementVersion": MODEL_ARTIFACT_PLACEMENT_VERSION,
        "state": "UNPLACED",
        "model": {
            "modelId": plan["model"]["modelId"],
            "expectedSha256": plan["artifact"]["expectedSha256"],
            "expectedSizeBytes": plan["artifact"]["expectedSizeBytes"],
            "format": plan["artifact"]["format"],
        },
        "target": {
            "directory": "models",
            "filename": "v1-5-pruned-emaonly.safetensors",
            "path": str(_TARGET_PATH),
        },
        "observed": {
            "pathExists": False,
            "hashObserved": False,
            "sizeObserved": False,
        },
        "governance": {
            "placementGrantsTrust": False,
            "placementGrantsExecutionAuthority": False,
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
        },
    }
    placement["modelArtifactPlacementHash"] = model_artifact_placement_hash(
        placement
    )
    validate_model_artifact_placement(placement)
    return placement


def validate_model_artifact_placement(
    placement: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(placement), schema)

    expected_hash = model_artifact_placement_hash(placement)
    if placement["modelArtifactPlacementHash"] != expected_hash:
        raise ValueError("Model artifact placement hash mismatch.")

    return placement
