"""Manual authorization gate for model artifact acquisition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.artifact_decision import (
    build_blocked_model_artifact_acquisition_decision,
)

MODEL_ARTIFACT_ACQUISITION_AUTHORIZATION_VERSION = (
    "OX-MODEL-ARTIFACT-ACQUISITION-AUTHORIZATION-1"
)
_SCHEMA_PATH = Path(
    "schemas/ox-model-artifact-acquisition-authorization-1.schema.json"
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_acquisition_authorization_hash(
    authorization: Mapping[str, Any],
) -> str:
    payload = dict(authorization)
    payload.pop("modelArtifactAcquisitionAuthorizationHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_blocked_model_artifact_acquisition_authorization(
    decision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a blocked authorization gate from the current artifact decision."""
    artifact_decision = (
        dict(decision)
        if decision is not None
        else build_blocked_model_artifact_acquisition_decision()
    )

    if artifact_decision["decision"] != "BLOCKED_NO_ARTIFACT":
        raise ValueError("Only blocked no-artifact decisions are supported.")
    if artifact_decision["governance"]["downloadAllowed"] is not False:
        raise ValueError("Artifact decision must not allow download.")
    if artifact_decision["governance"]["executionAllowed"] is not False:
        raise ValueError("Artifact decision must not allow execution.")

    authorization = {
        "authorizationVersion": (
            MODEL_ARTIFACT_ACQUISITION_AUTHORIZATION_VERSION
        ),
        "state": "BLOCKED_PENDING_MANUAL_APPROVAL",
        "source": {
            "decision": artifact_decision["decision"],
            "decisionHash": artifact_decision[
                "modelArtifactAcquisitionDecisionHash"
            ],
        },
        "authorization": {
            "manualApprovalRequired": True,
            "manualApprovalPresent": False,
            "approvedBy": None,
            "approvalTimestamp": None,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "trustGranted": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "authorizationGrantsAcquisitionAuthority": False,
            "authorizationGrantsExecutionAuthority": False,
        },
    }
    authorization["modelArtifactAcquisitionAuthorizationHash"] = (
        model_artifact_acquisition_authorization_hash(authorization)
    )
    validate_model_artifact_acquisition_authorization(authorization)
    return authorization


def validate_model_artifact_acquisition_authorization(
    authorization: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(authorization), schema)

    expected_hash = model_artifact_acquisition_authorization_hash(
        authorization
    )
    if authorization["modelArtifactAcquisitionAuthorizationHash"] != (
        expected_hash
    ):
        raise ValueError(
            "Model artifact acquisition authorization hash mismatch."
        )

    return authorization
