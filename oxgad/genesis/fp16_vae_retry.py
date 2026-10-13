"""External VAE preflight result and Genesis retry plan."""

from __future__ import annotations

from typing import Any

from oxgad.structure.canonical import canonical_sha256


APPROVAL_PHRASE = (
    "I APPROVE GENESIS-BATCH-0001 TOKEN 0001 "
    "FP16 VAE RETRY"
)


def _hashed(
    payload: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    return {
        **payload,
        field: canonical_sha256(payload),
    }


def build_external_vae_preflight_review() -> dict[str, Any]:
    payload = {
        "reviewVersion": (
            "OX-SD15-FP16-VAE-PREFLIGHT-REVIEW-1"
        ),
        "modelId": "OX-MODEL-002",
        "componentId": "OX-MODEL-002-VAE-FP16-1",
        "state": "PASSED_EXTERNAL_VAE_COMPATIBILITY",
        "runtimeEvidence": {
            "exitCode": 0,
            "durationSeconds": 95,
            "resolution": "256x256",
            "steps": 1,
            "batchSize": 1,
        },
        "media": {
            "sha256": (
                "sha256:"
                "ac8687f6f052e02b0623a73ff6d609a866d947fd"
                "2b4e4256ea6452d7460f8063"
            ),
            "sizeBytes": 138677,
            "format": "PNG",
            "colorType": "RGB",
            "bitsPerChannel": 8,
        },
        "visualReview": {
            "verticalBandingAbsent": True,
            "externalVaeDecodePassed": True,
            "artisticQualityEvaluated": False,
            "reasonArtisticQualityNotEvaluated": (
                "ONE_STEP_TECHNICAL_PREFLIGHT"
            ),
        },
        "diagnosis": {
            "embeddedQ4VaeDefectConfirmed": True,
            "externalFp16VaeRequired": True,
            "diffusionModelFailureConfirmed": False,
            "identityFailureConfirmed": False,
        },
        "governance": {
            "preflightPassed": True,
            "genesisRetryAutomaticallyAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    return _hashed(payload, "reviewHash")


def build_fp16_vae_genesis_retry_plan() -> dict[str, Any]:
    payload = {
        "retryPlanVersion": (
            "OX-GENESIS-FP16-VAE-RETRY-PLAN-1"
        ),
        "retryId": "GENESIS-0001-FP16-VAE-RETRY-1",
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "preflightReviewHash": (
            build_external_vae_preflight_review()["reviewHash"]
        ),
        "preserved": {
            "canonicalName": "Azhurak Primordialis",
            "modelId": "OX-MODEL-002",
            "modelHash": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "identityUnchanged": True,
            "dnaUnchanged": True,
            "resonanceUnchanged": True,
            "glyphUnchanged": True,
            "artSpecUnchanged": True,
            "promptUnchanged": True,
            "negativePromptUnchanged": True,
            "runtimeSeed": 5770080363699867898,
            "width": 384,
            "height": 384,
            "steps": 10,
            "sampler": "dpm++2m",
            "scheduler": "karras",
            "cfg": 7.0,
        },
        "externalVaeBinding": {
            "componentId": "OX-MODEL-002-VAE-FP16-1",
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
            "decodeMode": "NON_TILED",
        },
        "rejectedCandidates": [
            {
                "mediaHash": (
                    "sha256:"
                    "cf5f3567fee674760cfa22f79f66f0af4bd21b7d"
                    "d5deb354d119db21b32f316f"
                ),
                "vae": "EMBEDDED_Q4_0_TILED",
            },
            {
                "mediaHash": (
                    "sha256:"
                    "93ea7f78ca156cd640e1df2c7b67319504b941602"
                    "c9d9b32a25f22ae1c45ab87"
                ),
                "vae": "EMBEDDED_Q4_0_NON_TILED",
            },
        ],
        "limits": {
            "attempts": 1,
            "batchSize": 1,
            "timeoutSeconds": 2400,
            "minimumMemAvailableKB": 1800000,
            "criticalMemAvailableKB": 350000,
            "maximumThermalRaw": 80000,
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
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "upscaleAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    return _hashed(payload, "retryPlanHash")


__all__ = (
    "APPROVAL_PHRASE",
    "build_external_vae_preflight_review",
    "build_fp16_vae_genesis_retry_plan",
)
