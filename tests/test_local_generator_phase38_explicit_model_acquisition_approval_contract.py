import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_approval import (
    build_draft_model_artifact_acquisition_approval,
)
from oxgad.models.explicit_approval import (
    EXPLICIT_MODEL_ACQUISITION_APPROVAL_VERSION,
    build_not_granted_explicit_model_acquisition_approval,
    explicit_model_acquisition_approval_hash,
    validate_explicit_model_acquisition_approval,
)


def test_explicit_model_acquisition_approval_is_schema_valid_and_not_granted():
    approval = build_not_granted_explicit_model_acquisition_approval()
    schema = json.loads(
        Path(
            "schemas/ox-explicit-model-acquisition-approval-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(approval, schema)
    validate_explicit_model_acquisition_approval(approval)

    assert approval["explicitApprovalVersion"] == (
        EXPLICIT_MODEL_ACQUISITION_APPROVAL_VERSION
    )
    assert approval["state"] == "NOT_GRANTED"
    assert approval["approvalIntent"] == {
        "requiresExactUserApproval": True,
        "approvalPhrase": None,
        "approvalRecorded": False,
    }


def test_explicit_model_acquisition_approval_blocks_all_authority():
    approval = build_not_granted_explicit_model_acquisition_approval()

    assert approval["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "explicitApprovalGrantsAcquisitionAuthority": False,
        "explicitApprovalGrantsExecutionAuthority": False,
    }


def test_explicit_model_acquisition_approval_hash_is_deterministic():
    first = build_not_granted_explicit_model_acquisition_approval()
    second = build_not_granted_explicit_model_acquisition_approval()

    assert first == second
    assert first["explicitModelAcquisitionApprovalHash"] == (
        explicit_model_acquisition_approval_hash(first)
    )


def test_explicit_model_acquisition_approval_rejects_download_authority():
    approval = build_not_granted_explicit_model_acquisition_approval()
    approval["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_explicit_model_acquisition_approval(approval)


def test_explicit_model_acquisition_approval_rejects_hash_tampering():
    approval = build_not_granted_explicit_model_acquisition_approval()
    approval["explicitModelAcquisitionApprovalHash"] = (
        "sha256:" + "0" * 64
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_explicit_model_acquisition_approval(approval)


def test_explicit_model_acquisition_approval_requires_unapproved_draft():
    draft = build_draft_model_artifact_acquisition_approval()
    draft["approval"]["approved"] = True

    with pytest.raises(ValueError, match="cannot start from approval"):
        build_not_granted_explicit_model_acquisition_approval(draft)
