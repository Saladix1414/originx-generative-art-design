from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

PRODUCTION_MODEL_CANDIDATE_VERSION = (
    "OX-PRODUCTION-MODEL-CANDIDATE-1"
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-production-model-candidate-1.schema.json"
)


def build_z_image_production_candidate() -> dict[str, Any]:
    value = {
        "candidateVersion": PRODUCTION_MODEL_CANDIDATE_VERSION,
        "modelId": "OX-MODEL-001",
        "name": "Z-Image Q4_0",
        "canonicalRole": "PRIMARY_LOCAL_BASE_MODEL",
        "productionAlias": "OX-GENESIS-MODEL-1",
        "runtimeFamily": "stable-diffusion.cpp",
        "format": "GGUF",
        "quantization": "Q4_0",
        "license": "Apache-2.0",
        "selectionState": "CANDIDATE_PENDING_10_TOKEN_GATE",
        "artifact": {
            "filename": "z-image-q4_0.gguf",
            "expectedSizeBytes": None,
            "expectedSha256": None,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
        "benchmarkGate": {
            "requiredTokens": 10,
            "passed": False,
        },
    }
    return validate_production_model_candidate(value)


def validate_production_model_candidate(
    value: dict[str, Any],
) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(value, schema)
    return value
