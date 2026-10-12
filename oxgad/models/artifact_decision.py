"""Model artifact acquisition decision for local generator readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.artifact_evidence import (
    build_missing_model_artifact_evidence,
)

MODEL_ARTIFACT_ACQUISITION_DECISION_VERSION = (
    "OX-MODEL-ARTIFACT-ACQUISITION-DECISION-1"
)
_SCHEMA_PATH = Path(
    "schemas/ox-model-artifact-acquisition-decision-1.schema.json"
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_acquisition_decision_hash(
    decision: Mapping[str, Any],
) -> str:
    payload = dict(decision)
    payload.pop("modelArtifactAcquisitionDecisionHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_blocked_model_artifact_acquisition_decision(
    artifact_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a blocked acquisition decision from missing artifact evidence."""
    evidence = (
        dict(artifact_evidence)
        if artifact_evidence is not None
        else build_missing_model_artifact_evidence()
    )

    if evidence["state"] != "MISSING":
        raise ValueError("Only missing model artifact evidence is supported.")
    if evidence["governance"]["evidenceGrantsTrust"] is not False:
        raise ValueError("Artifact evidence must not grant trust.")
    if evidence["governance"]["executionAllowed"] is not False:
        raise ValueError("Artifact evidence must not grant execution.")

    decision = {
        "decisionVersion": MODEL_ARTIFACT_ACQUISITION_DECISION_VERSION,
        "decision": "BLOCKED_NO_ARTIFACT",
        "reasonCodes": [
            "MODEL_ARTIFACT_MISSING",
            "DOWNLOAD_NOT_AUTHORIZED",
            "INSTALLATION_NOT_AUTHORIZED",
            "TRUST_NOT_GRANTED",
            "EXECUTION_NOT_AUTHORIZED",
        ],
        "source": {
            "modelId": evidence["modelId"],
            "artifactEvidenceHash": evidence["modelArtifactEvidenceHash"],
            "artifactEvidenceState": evidence["state"],
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "trustGranted": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "decisionGrantsAcquisitionAuthority": False,
            "decisionGrantsExecutionAuthority": False,
        },
    }
    decision["modelArtifactAcquisitionDecisionHash"] = (
        model_artifact_acquisition_decision_hash(decision)
    )
    validate_model_artifact_acquisition_decision(decision)
    return decision


def validate_model_artifact_acquisition_decision(
    decision: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(decision), schema)

    expected_hash = model_artifact_acquisition_decision_hash(decision)
    if decision["modelArtifactAcquisitionDecisionHash"] != expected_hash:
        raise ValueError("Model artifact acquisition decision hash mismatch.")

    return decision
