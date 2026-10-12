"""Draft approval record for model artifact acquisition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.artifact_authorization import (
    build_blocked_model_artifact_acquisition_authorization,
)

MODEL_ARTIFACT_ACQUISITION_APPROVAL_VERSION = (
    "OX-MODEL-ARTIFACT-ACQUISITION-APPROVAL-1"
)
_SCHEMA_PATH = Path(
    "schemas/ox-model-artifact-acquisition-approval-1.schema.json"
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_artifact_acquisition_approval_hash(
    approval: Mapping[str, Any],
) -> str:
    payload = dict(approval)
    payload.pop("modelArtifactAcquisitionApprovalHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_draft_model_artifact_acquisition_approval(
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a draft approval that does not grant acquisition authority."""
    gate = (
        dict(authorization)
        if authorization is not None
        else build_blocked_model_artifact_acquisition_authorization()
    )

    if gate["state"] != "BLOCKED_PENDING_MANUAL_APPROVAL":
        raise ValueError("Approval draft requires a blocked authorization gate.")
    if gate["authorization"]["manualApprovalPresent"] is not False:
        raise ValueError("Approval draft requires missing manual approval.")
    if gate["governance"]["downloadAllowed"] is not False:
        raise ValueError("Authorization gate must not allow download.")
    if gate["governance"]["executionAllowed"] is not False:
        raise ValueError("Authorization gate must not allow execution.")

    approval = {
        "approvalVersion": MODEL_ARTIFACT_ACQUISITION_APPROVAL_VERSION,
        "state": "DRAFT_NOT_APPROVED",
        "source": {
            "authorizationState": gate["state"],
            "authorizationHash": gate[
                "modelArtifactAcquisitionAuthorizationHash"
            ],
        },
        "approval": {
            "approved": False,
            "approvedBy": None,
            "approvalTimestamp": None,
            "approvalScope": "MODEL_ARTIFACT_ACQUISITION_ONLY",
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "trustGranted": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "approvalGrantsAcquisitionAuthority": False,
            "approvalGrantsExecutionAuthority": False,
        },
    }
    approval["modelArtifactAcquisitionApprovalHash"] = (
        model_artifact_acquisition_approval_hash(approval)
    )
    validate_model_artifact_acquisition_approval(approval)
    return approval


def validate_model_artifact_acquisition_approval(
    approval: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(approval), schema)

    expected_hash = model_artifact_acquisition_approval_hash(approval)
    if approval["modelArtifactAcquisitionApprovalHash"] != expected_hash:
        raise ValueError("Model artifact acquisition approval hash mismatch.")

    return approval
