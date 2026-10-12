"""Operational status assessments for registered models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


MODEL_OPERATIONAL_STATUS_VERSION = (
    "OX-MODEL-OPERATIONAL-STATUS-1"
)

MODEL_OPERATIONAL_STATUS_SCHEMA_PATH = Path(
    "schemas/ox-model-operational-status-1.schema.json"
)


def validate_model_operational_status(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate a model operational status assessment."""
    schema = json.loads(
        MODEL_OPERATIONAL_STATUS_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_z_image_reference_model_status() -> dict[str, Any]:
    """Record Z-Image as preserved reference evidence."""
    value = {
        "statusVersion": MODEL_OPERATIONAL_STATUS_VERSION,
        "modelId": "OX-MODEL-001",
        "role": "REFERENCE_MODEL",
        "status": "BENCHMARKED",
        "localProductionStatus": (
            "NOT_SUITABLE_ON_CURRENT_DEVICE"
        ),
        "historicalRegistration": {
            "previousRole": "PRIMARY_LOCAL_BASE_MODEL",
            "previousProductionAlias": "OX-GENESIS-MODEL-1",
            "preserved": True,
            "supersededForLocalProduction": True,
        },
        "artifacts": {
            "preserved": True,
            "deletionAllowed": False,
            "manifestReference": (
                "OX-Z-IMAGE-ARTIFACT-MANIFEST-1"
            ),
            "acquisitionReceiptReference": (
                "docs/local-generator/"
                "phase70-z-image-acquisition-receipt.json"
            ),
        },
        "benchmarkEvidence": {
            "runtimePreflightPerformed": True,
            "result": "FAILED_RUNTIME_STABILITY",
            "failureStage": (
                "DIFFUSION_TRANSFORMER_TENSOR_LOADING"
            ),
            "imageProduced": False,
            "currentDeviceSuitable": False,
        },
        "provenance": {
            "sourcePreserved": True,
            "licensePreserved": True,
            "hashesPreserved": True,
            "sizesPreserved": True,
            "benchmarkEvidencePreserved": True,
        },
        "governance": {
            "productionAliasAssigned": False,
            "executionAllowed": False,
            "automaticRetryAllowed": False,
            "batchGenerationAllowed": False,
            "canonicalizationAllowed": False,
        },
    }

    validate_model_operational_status(value)
    return value
