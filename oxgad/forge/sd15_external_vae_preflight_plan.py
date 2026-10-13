"""Single preflight plan for the official SD 1.5 FP16 VAE."""

from __future__ import annotations

from typing import Any

from oxgad.structure.canonical import canonical_sha256


APPROVAL_PHRASE = (
    "I APPROVE OX-MODEL-002 SD15 FP16 "
    "VAE SINGLE PREFLIGHT"
)


def build_external_vae_preflight_plan() -> dict[str, Any]:
    payload = {
        "planVersion": (
            "OX-SD15-EXTERNAL-VAE-PREFLIGHT-PLAN-1"
        ),
        "modelId": "OX-MODEL-002",
        "componentId": "OX-MODEL-002-VAE-FP16-1",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "purpose": "SINGLE_EXTERNAL_VAE_PREFLIGHT",
        "artifacts": {
            "model": {
                "path": (
                    "models/sd15/"
                    "stable-diffusion-v1-5-pruned-emaonly-Q4_0.gguf"
                ),
                "sha256": (
                    "sha256:"
                    "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                    "fe0fa9af6c64c4829022261f"
                ),
            },
            "vae": {
                "path": (
                    "models/sd15/vae/"
                    "sd15-official-vae-fp16.safetensors"
                ),
                "sha256": (
                    "sha256:"
                    "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
                    "29bb4d81890039d2aa16dd7c"
                ),
                "precision": "FP16",
            },
        },
        "request": {
            "width": 256,
            "height": 256,
            "steps": 1,
            "batchSize": 1,
            "seed": 1001,
            "threads": 4,
            "cfg": 7.0,
            "sampler": "euler_a",
            "paramsBackend": "disk",
            "mmap": True,
            "vaeDecodeMode": "NON_TILED",
            "output": (
                "output/candidates/"
                "0001-sd15-fp16-vae-preflight.png"
            ),
        },
        "monitoring": {
            "timeoutSeconds": 900,
            "minimumMemAvailableKBBeforeStart": 1800000,
            "criticalMemAvailableKB": 350000,
            "maximumThermalRaw": 80000,
            "recordMemory": True,
            "recordThermals": True,
            "recordRuntimeLog": True,
        },
        "successCriteria": {
            "runtimeExitCode": 0,
            "outputRequired": True,
            "outputFormat": "PNG",
            "outputColorType": "RGB",
            "outputBitsPerChannel": 8,
            "expectedWidth": 256,
            "expectedHeight": 256,
            "verticalBandingAbsentRequired": True,
            "manualVisualReviewRequired": True,
        },
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": APPROVAL_PHRASE,
        },
        "governance": {
            "planGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "genesisRetryAllowed": False,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }

    return {
        **payload,
        "planHash": canonical_sha256(payload),
    }


__all__ = (
    "APPROVAL_PHRASE",
    "build_external_vae_preflight_plan",
)
