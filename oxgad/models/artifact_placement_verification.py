"""Read-only verification for model artifact placement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.artifact_placement import (
    build_unplaced_model_artifact_placement,
)

MODEL_ARTIFACT_PLACEMENT_VERIFICATION_VERSION = (
    "OX-MODEL-ARTIFACT-PLACEMENT-VERIFICATION-1"
)
_SCHEMA_PATH = Path(
    "schemas/ox-model-artifact-placement-verification-1.schema.json"
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_placement_verification_hash(
    verification: Mapping[str, Any],
) -> str:
    payload = dict(verification)
    payload.pop("modelArtifactPlacementVerificationHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_missing_model_artifact_placement_verification(
    placement: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the declared artifact target without reading model content."""
    source = (
        dict(placement)
        if placement is not None
        else build_unplaced_model_artifact_placement()
    )

    if source["state"] != "UNPLACED":
        raise ValueError("Missing verification requires unplaced placement.")

    target_path = source["target"]["path"]
    path = Path(target_path)

    path_exists = path.exists()
    is_file = path.is_file()
    if path_exists or is_file:
        raise ValueError("Expected missing model artifact target.")

    verification = {
        "verificationVersion": (
            MODEL_ARTIFACT_PLACEMENT_VERIFICATION_VERSION
        ),
        "state": "MISSING",
        "source": {
            "placementState": source["state"],
            "placementHash": source["modelArtifactPlacementHash"],
        },
        "target": {
            "path": target_path,
        },
        "observed": {
            "pathExists": False,
            "isFile": False,
            "sizeBytes": None,
        },
        "governance": {
            "verificationGrantsTrust": False,
            "verificationGrantsExecutionAuthority": False,
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
        },
    }
    verification["modelArtifactPlacementVerificationHash"] = (
        model_artifact_placement_verification_hash(verification)
    )
    validate_model_artifact_placement_verification(verification)
    return verification


def validate_model_artifact_placement_verification(
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(verification), schema)

    expected_hash = model_artifact_placement_verification_hash(verification)
    if verification["modelArtifactPlacementVerificationHash"] != expected_hash:
        raise ValueError("Model artifact placement verification hash mismatch.")

    return verification
