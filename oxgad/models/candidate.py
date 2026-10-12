from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

MODEL_CANDIDATE_VERSION = "OX-MODEL-CANDIDATE-1"

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-candidate-1.schema.json"
)


def validate_model_candidate(value: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(value, schema)
    return value


def build_model_candidate(
    *,
    model_id: str,
    name: str,
    family: str,
    artifact_format: str,
    artifact_size_bytes: int,
    artifact_sha256: str,
    runtime_family: str,
) -> dict[str, Any]:
    candidate = {
        "candidateVersion": MODEL_CANDIDATE_VERSION,
        "modelId": model_id,
        "name": name,
        "family": family,
        "artifact": {
            "format": artifact_format,
            "expectedSizeBytes": artifact_size_bytes,
            "expectedSha256": artifact_sha256,
        },
        "runtimeCompatibility": {
            "runtimeFamily": runtime_family,
            "state": "UNASSESSED",
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
        },
    }
    return validate_model_candidate(candidate)
