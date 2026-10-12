"""Authorized download plan for SD 1.5 Q4_0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


SD15_DOWNLOAD_APPROVAL_PHRASE = (
    "I APPROVE OX-MODEL-002 SD15 Q4_0 ARTIFACT DOWNLOAD"
)

SD15_AUTHORIZED_DOWNLOAD_PLAN_VERSION = (
    "OX-SD15-AUTHORIZED-DOWNLOAD-PLAN-1"
)

SD15_AUTHORIZED_DOWNLOAD_PLAN_SCHEMA_PATH = Path(
    "schemas/ox-sd15-authorized-download-plan-1.schema.json"
)


def validate_sd15_authorized_download_plan(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SD15_AUTHORIZED_DOWNLOAD_PLAN_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_sd15_authorized_download_plan() -> dict[str, Any]:
    value = {
        "planVersion": (
            SD15_AUTHORIZED_DOWNLOAD_PLAN_VERSION
        ),
        "modelId": "OX-MODEL-002",
        "selectedPath": "AUTHORIZED_DOWNLOAD",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "artifact": {
            "repository": (
                "second-state/stable-diffusion-v1-5-GGUF"
            ),
            "revision": (
                "031b5f5df991f511b3f5fa8fed6d99048ababb69"
            ),
            "filename": (
                "stable-diffusion-v1-5-"
                "pruned-emaonly-Q4_0.gguf"
            ),
            "targetPath": (
                "models/sd15/"
                "stable-diffusion-v1-5-"
                "pruned-emaonly-Q4_0.gguf"
            ),
            "format": "GGUF",
            "quantization": "Q4_0",
            "expectedSizeBytes": 1566768416,
            "expectedSha256": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "license": "CreativeML OpenRAIL-M",
        },
        "requirements": {
            "minimumFreeStorageBytes": 3133536832,
            "storageCheckRequired": True,
            "licenseReviewRequired": True,
            "runtimeCompatibilityRequired": True,
            "hashVerificationRequired": True,
            "sizeVerificationRequired": True,
            "partialDownloadRequired": True,
            "atomicPromotionRequired": True,
        },
        "approval": {
            "required": True,
            "present": False,
            "requiredPhrase": SD15_DOWNLOAD_APPROVAL_PHRASE,
            "phraseAccepted": False,
        },
        "postDownload": {
            "runtimeExecutionAllowed": False,
            "singlePreflightApprovalRequired": True,
            "benchmarkApprovalRequired": True,
            "automaticBenchmarkAllowed": False,
        },
        "governance": {
            "planGrantsDownloadAuthority": False,
            "downloadAllowed": False,
            "executionAllowed": False,
            "batchGenerationAllowed": False,
            "canonicalizationAllowed": False,
        },
    }

    validate_sd15_authorized_download_plan(value)
    return value
