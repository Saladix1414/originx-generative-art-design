"""Explicit user approval boundary for model acquisition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.models.artifact_approval import (
    build_draft_model_artifact_acquisition_approval,
)

EXPLICIT_MODEL_ACQUISITION_APPROVAL_VERSION = (
    "OX-EXPLICIT-MODEL-ACQUISITION-APPROVAL-1"
)
_SCHEMA_PATH = Path(
    "schemas/ox-explicit-model-acquisition-approval-1.schema.json"
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def explicit_model_acquisition_approval_hash(
    approval: Mapping[str, Any],
) -> str:
    payload = dict(approval)
    payload.pop("explicitModelAcquisitionApprovalHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_not_granted_explicit_model_acquisition_approval(
    draft_approval: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an explicit approval boundary that grants no authority."""
    draft = (
        dict(draft_approval)
        if draft_approval is not None
        else build_draft_model_artifact_acquisition_approval()
    )

    if draft["state"] != "DRAFT_NOT_APPROVED":
        raise ValueError("Explicit approval requires an unapproved draft.")
    if draft["approval"]["approved"] is not False:
        raise ValueError("Explicit approval cannot start from approval.")
    if draft["governance"]["downloadAllowed"] is not False:
        raise ValueError("Draft approval must not allow download.")
    if draft["governance"]["executionAllowed"] is not False:
        raise ValueError("Draft approval must not allow execution.")

    approval = {
        "explicitApprovalVersion": (
            EXPLICIT_MODEL_ACQUISITION_APPROVAL_VERSION
        ),
        "state": "NOT_GRANTED",
        "source": {
            "draftApprovalState": draft["state"],
            "draftApprovalHash": draft[
                "modelArtifactAcquisitionApprovalHash"
            ],
        },
        "approvalIntent": {
            "requiresExactUserApproval": True,
            "approvalPhrase": None,
            "approvalRecorded": False,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "trustGranted": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "explicitApprovalGrantsAcquisitionAuthority": False,
            "explicitApprovalGrantsExecutionAuthority": False,
        },
    }
    approval["explicitModelAcquisitionApprovalHash"] = (
        explicit_model_acquisition_approval_hash(approval)
    )
    validate_explicit_model_acquisition_approval(approval)
    return approval


def validate_explicit_model_acquisition_approval(
    approval: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(approval), schema)

    expected_hash = explicit_model_acquisition_approval_hash(approval)
    if approval["explicitModelAcquisitionApprovalHash"] != expected_hash:
        raise ValueError("Explicit model acquisition approval hash mismatch.")

    return approval
