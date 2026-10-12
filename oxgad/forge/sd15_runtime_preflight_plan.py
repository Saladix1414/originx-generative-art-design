"""Conservative runtime preflight plan for SD 1.5 Q4_0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


SD15_RUNTIME_PREFLIGHT_APPROVAL_PHRASE = (
    "I APPROVE OX-MODEL-002 SD15 SINGLE RUNTIME PREFLIGHT"
)

SD15_RUNTIME_PREFLIGHT_PLAN_VERSION = (
    "OX-SD15-RUNTIME-PREFLIGHT-PLAN-1"
)

SD15_RUNTIME_PREFLIGHT_PLAN_SCHEMA_PATH = Path(
    "schemas/ox-sd15-runtime-preflight-plan-1.schema.json"
)


def validate_sd15_runtime_preflight_plan(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SD15_RUNTIME_PREFLIGHT_PLAN_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_sd15_runtime_preflight_plan() -> dict[str, Any]:
    value = {
        "planVersion": SD15_RUNTIME_PREFLIGHT_PLAN_VERSION,
        "modelId": "OX-MODEL-002",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "purpose": "SINGLE_RUNTIME_PREFLIGHT",
        "artifact": {
            "path": (
                "models/sd15/"
                "stable-diffusion-v1-5-"
                "pruned-emaonly-Q4_0.gguf"
            ),
            "expectedSizeBytes": 1566768416,
            "expectedSha256": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "verificationRequiredBeforeExecution": True,
        },
        "runtime": {
            "family": "stable-diffusion.cpp",
            "commit": (
                "792bcd344c3fa4d14143b240d5f6cbb324583b18"
            ),
            "binary": (
                "/root/stable-diffusion.cpp/build/bin/sd-cli"
            ),
            "binarySha256": (
                "sha256:"
                "a57f5f195e0dea9b3d0461af92e528c7c25a6a98"
                "f0bf2edc771a2f5835252e42"
            ),
        },
        "request": {
            "width": 256,
            "height": 256,
            "steps": 1,
            "batchSize": 1,
            "seed": 1001,
            "threads": 4,
            "cfgScale": 7.0,
            "samplingMethod": "euler",
            "paramsBackend": "disk",
            "mmap": True,
            "vaeTiling": True,
            "vaeTileSize": "128x128",
            "prompt": (
                "a simple centered ancient obsidian relic, "
                "neutral background, studio lighting"
            ),
            "output": (
                "output/candidates/"
                "0001-sd15-runtime-preflight.png"
            ),
        },
        "monitoring": {
            "memoryRequired": True,
            "swapRequired": True,
            "generationTimeRequired": True,
            "thermalReadingsRequiredWhenAvailable": True,
            "runtimeLogRequired": True,
            "timeoutSeconds": 1800,
        },
        "successCriteria": {
            "processExitCode": 0,
            "outputImageRequired": True,
            "deviceRestartAllowed": False,
            "runtimeCrashAllowed": False,
            "artifactMutationAllowed": False,
        },
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": (
                SD15_RUNTIME_PREFLIGHT_APPROVAL_PHRASE
            ),
        },
        "governance": {
            "planGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "benchmarkTokensAllowed": False,
            "batchGenerationAllowed": False,
            "canonicalizationAllowed": False,
            "finalProductionStatusGranted": False,
        },
    }

    validate_sd15_runtime_preflight_plan(value)
    return value
