"""Optimized conservative render profile for Genesis token #0001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.structure.canonical import canonical_sha256


PROFILE_VERSION = "OX-GENESIS-RENDER-PROFILE-2"
PROFILE_ID = "GENESIS-SD15-CONSERVATIVE-384-V2"
GATE_VERSION = "OX-GENESIS-TOKEN-EXECUTION-GATE-1"
INTERRUPTION_VERSION = "OX-GENESIS-RENDER-INTERRUPTION-1"

APPROVAL_PHRASE = (
    "I APPROVE GENESIS-BATCH-0001 TOKEN 0001 "
    "RENDER PROFILE 2"
)

PROFILE_SCHEMA = Path(
    "schemas/ox-genesis-render-profile-2.schema.json"
)
GATE_SCHEMA = Path(
    "schemas/ox-genesis-token-execution-gate-1.schema.json"
)
INTERRUPTION_SCHEMA = Path(
    "schemas/ox-genesis-render-interruption-1.schema.json"
)

MODEL_HASH = (
    "sha256:"
    "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
    "fe0fa9af6c64c4829022261f"
)


def _validate(
    value: Mapping[str, Any],
    schema_path: Path,
) -> Mapping[str, Any]:
    schema = json.loads(
        schema_path.read_text(encoding="utf-8")
    )
    jsonschema.validate(dict(value), schema)
    return value


def _hashed(payload: dict[str, Any], field: str) -> dict[str, Any]:
    return {
        **payload,
        field: canonical_sha256(payload),
    }


def build_render_profile_2() -> dict[str, Any]:
    payload = {
        "profileVersion": PROFILE_VERSION,
        "profileId": PROFILE_ID,
        "scope": {
            "batchId": "GENESIS-BATCH-0001",
            "tokenIds": [1],
            "batchSize": 1,
            "sequentialOnly": True,
        },
        "model": {
            "modelId": "OX-MODEL-002",
            "productionAlias": "OX-GENESIS-MODEL-1",
            "modelHash": MODEL_HASH,
            "quantization": "Q4_0",
            "runtime": "stable-diffusion.cpp",
        },
        "render": {
            "width": 384,
            "height": 384,
            "steps": 10,
            "sampler": "dpm++2m",
            "scheduler": "karras",
            "cfg": 7.0,
            "threads": 4,
            "paramsBackend": "disk",
            "mmap": True,
            "vaeTiling": True,
            "vaeTileSize": "128x128",
        },
        "output": {
            "format": "PNG",
            "colorType": "RGB",
            "bitsPerChannel": 8,
            "lossless": True,
            "candidateOnly": True,
            "canonical": False,
        },
        "detailPolicy": {
            "authorityOrder": ["MACRO", "MESO", "MICRO"],
            "qualityTarget": 92,
            "manualReviewRequired": True,
            "upscale": {
                "state": "DEFERRED_UNTIL_QUALITY_APPROVAL",
                "targetWidth": 1024,
                "targetHeight": 1024,
                "candidateAndUpscaleHashesRequired": True,
            },
        },
        "identityPreservation": {
            "identityUnchanged": True,
            "dnaUnchanged": True,
            "resonanceUnchanged": True,
            "glyphUnchanged": True,
            "artSpecUnchanged": True,
            "akashicHistoryPreserved": True,
            "renderProfileVersionedSeparately": True,
        },
    }
    value = _hashed(payload, "profileHash")
    _validate(value, PROFILE_SCHEMA)
    return value


def build_interruption_evidence() -> dict[str, Any]:
    payload = {
        "evidenceVersion": INTERRUPTION_VERSION,
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "state": "INTERRUPTED_BY_USER",
        "attempt": {
            "width": 512,
            "height": 512,
            "steps": 12,
            "sampler": "euler_a",
            "scheduler": "discrete",
            "cfg": 7.0,
        },
        "observation": {
            "lastTelemetryElapsedSeconds": 771,
            "minimumObservedMemAvailableKB": 644212,
            "candidateImageProduced": False,
            "candidateMediaHash": None,
            "runtimeLoadSucceeded": True,
            "samplingProgressObserved": "5/12",
        },
        "classification": {
            "tokenFailure": False,
            "modelFailure": False,
            "qualityFailure": False,
            "reason": "USER_REQUESTED_RENDER_PROFILE_OPTIMIZATION",
            "retryPreservesTokenIdentity": True,
        },
        "governance": {
            "canonicalArtworkCreated": False,
            "qualityReviewPerformed": False,
            "automaticRetryAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    value = _hashed(payload, "evidenceHash")
    _validate(value, INTERRUPTION_SCHEMA)
    return value


def build_token_0001_profile_2_gate() -> dict[str, Any]:
    profile = build_render_profile_2()
    payload = {
        "gateVersion": GATE_VERSION,
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "profileId": PROFILE_ID,
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": APPROVAL_PHRASE,
        },
        "limits": {
            "tokens": 1,
            "batchSize": 1,
            "width": 384,
            "height": 384,
            "steps": 10,
            "timeoutSeconds": 3600,
            "minimumMemAvailableKB": 1200000,
            "maximumThermalRaw": 80000,
            "profileHash": profile["profileHash"],
        },
        "governance": {
            "gateGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    value = _hashed(payload, "gateHash")
    _validate(value, GATE_SCHEMA)
    return value


__all__ = (
    "APPROVAL_PHRASE",
    "PROFILE_ID",
    "PROFILE_VERSION",
    "build_interruption_evidence",
    "build_render_profile_2",
    "build_token_0001_profile_2_gate",
)
