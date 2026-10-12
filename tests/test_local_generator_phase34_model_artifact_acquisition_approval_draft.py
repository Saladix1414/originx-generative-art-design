import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_approval import (
    MODEL_ARTIFACT_ACQUISITION_APPROVAL_VERSION,
    build_draft_model_artifact_acquisition_approval,
    model_artifact_acquisition_approval_hash,
    validate_model_artifact_acquisition_approval,
)
from oxgad.models.artifact_authorization import (
    build_blocked_model_artifact_acquisition_authorization,
)


def test_model_artifact_acquisition_approval_draft_is_schema_valid():
    approval = build_draft_model_artifact_acquisition_approval()
    schema = json.loads(
        Path(
            "schemas/ox-model-artifact-acquisition-approval-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(approval, schema)
    validate_model_artifact_acquisition_approval(approval)

    assert approval["approvalVersion"] == (
        MODEL_ARTIFACT_ACQUISITION_APPROVAL_VERSION
    )
    assert approval["state"] == "DRAFT_NOT_APPROVED"
    assert approval["source"]["authorizationState"] == (
        "BLOCKED_PENDING_MANUAL_APPROVAL"
    )


def test_model_artifact_acquisition_approval_draft_does_not_approve():
    approval = build_draft_model_artifact_acquisition_approval()

    assert approval["approval"] == {
        "approved": False,
        "approvedBy": None,
        "approvalTimestamp": None,
        "approvalScope": "MODEL_ARTIFACT_ACQUISITION_ONLY",
    }
    assert approval["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "approvalGrantsAcquisitionAuthority": False,
        "approvalGrantsExecutionAuthority": False,
    }


def test_model_artifact_acquisition_approval_draft_hash_is_deterministic():
    first = build_draft_model_artifact_acquisition_approval()
    second = build_draft_model_artifact_acquisition_approval()

    assert first == second
    assert first["modelArtifactAcquisitionApprovalHash"] == (
        model_artifact_acquisition_approval_hash(first)
    )


def test_model_artifact_acquisition_approval_rejects_download_authority():
    approval = build_draft_model_artifact_acquisition_approval()
    approval["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_acquisition_approval(approval)


def test_model_artifact_acquisition_approval_rejects_hash_tampering():
    approval = build_draft_model_artifact_acquisition_approval()
    approval["modelArtifactAcquisitionApprovalHash"] = (
        "sha256:" + "0" * 64
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_acquisition_approval(approval)


def test_model_artifact_acquisition_approval_requires_blocked_authorization():
    authorization = build_blocked_model_artifact_acquisition_authorization()
    authorization["authorization"]["manualApprovalPresent"] = True

    with pytest.raises(ValueError, match="missing manual approval"):
        build_draft_model_artifact_acquisition_approval(authorization)
