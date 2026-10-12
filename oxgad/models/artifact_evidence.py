"""Model artifact evidence for local generator readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.acquisition import build_first_local_model_plan

MODEL_ARTIFACT_EVIDENCE_VERSION = "OX-MODEL-ARTIFACT-EVIDENCE-1"
_SCHEMA_PATH = Path("schemas/ox-model-artifact-evidence-1.schema.json")


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_evidence_hash(
    evidence: Mapping[str, Any],
) -> str:
    payload = dict(evidence)
    payload.pop("modelArtifactEvidenceHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_missing_model_artifact_evidence() -> dict[str, Any]:
    """Return evidence that the declared first local model is not present."""
    plan = build_first_local_model_plan()
    evidence = {
        "evidenceVersion": MODEL_ARTIFACT_EVIDENCE_VERSION,
        "state": "MISSING",
        "modelId": plan["model"]["modelId"],
        "expectedArtifact": {
            "format": plan["artifact"]["format"],
            "sha256": plan["artifact"]["expectedSha256"],
            "sizeBytes": plan["artifact"]["expectedSizeBytes"],
        },
        "observedArtifact": {
            "path": None,
            "format": None,
            "sha256": None,
            "sizeBytes": None,
        },
        "checks": {
            "artifactPresent": False,
            "formatMatches": False,
            "hashMatches": False,
            "sizeMatches": False,
        },
        "governance": {
            "evidenceGrantsTrust": False,
            "evidenceGrantsExecutionAuthority": False,
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
        },
    }
    evidence["modelArtifactEvidenceHash"] = model_artifact_evidence_hash(evidence)
    validate_model_artifact_evidence(evidence)
    return evidence


def validate_model_artifact_evidence(
    evidence: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(evidence), schema)
    expected_hash = model_artifact_evidence_hash(evidence)
    if evidence["modelArtifactEvidenceHash"] != expected_hash:
        raise ValueError("Model artifact evidence hash mismatch.")
    return evidence
