"""Quality rejection and technical retry gate for Genesis #0001."""

from __future__ import annotations

from typing import Any

from oxgad.structure.canonical import canonical_sha256


RETRY_APPROVAL_PHRASE = (
    "I APPROVE GENESIS-BATCH-0001 TOKEN 0001 "
    "TECHNICAL RETRY 1"
)

CANDIDATE_HASH = (
    "sha256:"
    "cf5f3567fee674760cfa22f79f66f0af4bd21b7d"
    "d5deb354d119db21b32f316f"
)

PROFILE_HASH = (
    "sha256:"
    "7876bca555619484b292a02ca5d27e65022d9ef1"
    "a27c297f29f9a6613e05decb"
)


def _hashed(
    payload: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    return {
        **payload,
        field: canonical_sha256(payload),
    }


def build_candidate_rejection() -> dict[str, Any]:
    payload = {
        "reviewVersion": "OX-GENESIS-QUALITY-REVIEW-1",
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "candidateMediaHash": CANDIDATE_HASH,
        "state": "REJECTED_TECHNICAL_ARTIFACT",
        "qualityTarget": 92,
        "scores": {
            "anatomyScore": 0,
            "silhouetteScore": 0,
            "compositionScore": 0,
            "traitComplianceScore": 0,
            "materialScore": 0,
            "detailScore": 0,
            "identityConsistencyScore": 0,
            "visualGrammarScore": 0,
            "artifactScore": 0,
            "diversityScore": None,
        },
        "evidence": {
            "pngIntegrityPassed": True,
            "rgb8PixelDecodePassed": True,
            "width": 384,
            "height": 384,
            "verticalBandingCritical": True,
            "subjectOnlyFaintlyVisible": True,
            "visualAssessmentPossible": False,
            "suspectedFailureStage": "VAE_TILED_DECODE",
            "rootCauseConfirmed": False,
        },
        "decision": {
            "qualityGatePassed": False,
            "canonicalApproved": False,
            "upscaleAllowed": False,
            "automaticRetryAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
        "identityPreservation": {
            "tokenIdentityFailed": False,
            "identityUnchanged": True,
            "dnaUnchanged": True,
            "resonanceUnchanged": True,
            "glyphUnchanged": True,
            "artSpecUnchanged": True,
            "seedUnchanged": True,
        },
    }
    return _hashed(payload, "reviewHash")


def build_technical_retry_plan() -> dict[str, Any]:
    payload = {
        "retryPlanVersion": (
            "OX-GENESIS-TECHNICAL-RETRY-PLAN-1"
        ),
        "retryId": "GENESIS-0001-TECHNICAL-RETRY-1",
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "sourceCandidateMediaHash": CANDIDATE_HASH,
        "sourceProfileHash": PROFILE_HASH,
        "classification": {
            "retryType": "TECHNICAL_DECODE_ISOLATION",
            "identityReplacement": False,
            "creativeReroll": False,
            "modelSubstitution": False,
        },
        "preserved": {
            "modelId": "OX-MODEL-002",
            "modelHash": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "width": 384,
            "height": 384,
            "steps": 10,
            "sampler": "dpm++2m",
            "scheduler": "karras",
            "cfg": 7.0,
            "runtimeSeed": 5770080363699867898,
            "prompt": "UNCHANGED_FROM_PROFILE2_ATTEMPT",
            "negativePrompt": "UNCHANGED_FROM_PROFILE2_ATTEMPT",
        },
        "singleChange": {
            "component": "VAE_DECODE",
            "previousMode": "TILED_128X128",
            "retryMode": "NON_TILED",
            "removeArguments": [
                "--vae-tiling",
                "--vae-tile-size",
                "128x128",
            ],
        },
        "limits": {
            "attempts": 1,
            "batchSize": 1,
            "timeoutSeconds": 3600,
            "minimumMemAvailableKB": 1800000,
            "criticalMemAvailableKB": 350000,
            "maximumThermalRaw": 80000,
        },
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": RETRY_APPROVAL_PHRASE,
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
    "RETRY_APPROVAL_PHRASE",
    "build_candidate_rejection",
    "build_technical_retry_plan",
)
