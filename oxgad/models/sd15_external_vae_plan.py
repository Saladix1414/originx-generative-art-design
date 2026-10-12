"""Authorized-download plan for SD 1.5 official FP16 VAE."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.structure.canonical import canonical_sha256


PLAN_VERSION = "OX-SD15-EXTERNAL-VAE-DOWNLOAD-PLAN-1"
COMPONENT_ID = "OX-MODEL-002-VAE-FP16-1"

APPROVAL_PHRASE = (
    "I APPROVE OX-MODEL-002 SD15 FP16 "
    "VAE ARTIFACT DOWNLOAD"
)

SCHEMA_PATH = Path(
    "schemas/ox-sd15-external-vae-download-plan-1.schema.json"
)


def validate_external_vae_download_plan(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_external_vae_download_plan() -> dict[str, Any]:
    payload = {
        "planVersion": PLAN_VERSION,
        "modelId": "OX-MODEL-002",
        "componentId": COMPONENT_ID,
        "state": "PENDING_EXPLICIT_APPROVAL",
        "purpose": "REPLACE_DEFECTIVE_EMBEDDED_Q4_0_VAE",
        "source": {
            "provider": "HUGGING_FACE",
            "repository": (
                "stable-diffusion-v1-5/"
                "stable-diffusion-v1-5"
            ),
            "revision": (
                "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
            ),
            "filename": (
                "vae/diffusion_pytorch_model.fp16.safetensors"
            ),
            "license": "CreativeML OpenRAIL-M",
            "gated": False,
        },
        "artifact": {
            "targetPath": (
                "models/sd15/vae/"
                "sd15-official-vae-fp16.safetensors"
            ),
            "format": "safetensors",
            "precision": "FP16",
            "expectedSizeBytes": 167335342,
            "expectedSha256": (
                "sha256:"
                "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
                "29bb4d81890039d2aa16dd7c"
            ),
        },
        "runtimeCompatibility": {
            "runtime": "stable-diffusion.cpp",
            "runtimeSupportsExternalVae": True,
            "cliArgument": "--vae",
            "sd15LatentFormatExpected": True,
            "compatibilityState": "SOURCE_AUDITED_NOT_EXECUTED",
        },
        "expectedMemoryProfile": {
            "artifactBytes": 167335342,
            "precision": "FP16",
            "candidateResolution": "384x384",
            "batchSize": 1,
            "nonTiledDecodePreferredForIsolation": True,
            "minimumMemAvailableKBForPreflight": 1800000,
            "memoryCompatibilityState": "REQUIRES_PREFLIGHT",
        },
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": APPROVAL_PHRASE,
        },
        "postDownload": {
            "verifySize": True,
            "verifySha256": True,
            "recordAcquisitionReceipt": True,
            "singlePreflightRequired": True,
            "preflightResolution": "256x256",
            "preflightSteps": 1,
            "genesisRetryRequiresSeparateApproval": True,
        },
        "governance": {
            "planGrantsDownloadAuthority": False,
            "downloadAllowed": False,
            "executionAllowed": False,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }

    value = {
        **payload,
        "planHash": canonical_sha256(payload),
    }
    validate_external_vae_download_plan(value)
    return value


__all__ = (
    "APPROVAL_PHRASE",
    "COMPONENT_ID",
    "PLAN_VERSION",
    "build_external_vae_download_plan",
    "validate_external_vae_download_plan",
)
