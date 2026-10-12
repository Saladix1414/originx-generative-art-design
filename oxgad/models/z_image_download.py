from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

Z_IMAGE_DOWNLOAD_PLAN_VERSION = (
    "OX-Z-IMAGE-AUTHORIZED-DOWNLOAD-PLAN-1"
)

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-z-image-authorized-download-plan-1.schema.json"
)


def build_blocked_z_image_download_plan() -> dict[str, Any]:
    value = {
        "planVersion": Z_IMAGE_DOWNLOAD_PLAN_VERSION,
        "modelId": "OX-MODEL-001",
        "state": "BLOCKED_PENDING_RAM_GATE_AND_EXPLICIT_APPROVAL",
        "checks": {
            "sourceVerified": True,
            "licenseVerified": True,
            "runtimeCompatibilityVerified": True,
            "storageCapacityVerified": True,
            "ramBenchmarkPassed": False,
        },
        "approval": {
            "explicitApprovalRequired": True,
            "explicitApprovalPresent": False,
        },
        "download": {
            "artifactCount": 3,
            "expectedSizeBytes": 6348318966,
            "minimumFreeStorageBytes": 12000000000,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
    }
    return validate_z_image_download_plan(value)


def validate_z_image_download_plan(
    value: dict[str, Any],
) -> dict[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(value, schema)
    return value
