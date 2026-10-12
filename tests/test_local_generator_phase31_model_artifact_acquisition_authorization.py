import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.artifact_authorization import (
    MODEL_ARTIFACT_ACQUISITION_AUTHORIZATION_VERSION,
    build_blocked_model_artifact_acquisition_authorization,
    model_artifact_acquisition_authorization_hash,
    validate_model_artifact_acquisition_authorization,
)
from oxgad.models.artifact_decision import (
    build_blocked_model_artifact_acquisition_decision,
)


def test_model_artifact_acquisition_authorization_is_schema_valid_and_blocked():
    authorization = build_blocked_model_artifact_acquisition_authorization()
    schema = json.loads(
        Path(
            "schemas/ox-model-artifact-acquisition-authorization-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(authorization, schema)
    validate_model_artifact_acquisition_authorization(authorization)

    assert authorization["authorizationVersion"] == (
        MODEL_ARTIFACT_ACQUISITION_AUTHORIZATION_VERSION
    )
    assert authorization["state"] == "BLOCKED_PENDING_MANUAL_APPROVAL"
    assert authorization["source"]["decision"] == "BLOCKED_NO_ARTIFACT"
    assert authorization["authorization"] == {
        "manualApprovalRequired": True,
        "manualApprovalPresent": False,
        "approvedBy": None,
        "approvalTimestamp": None,
    }


def test_model_artifact_acquisition_authorization_blocks_download_and_execution():
    authorization = build_blocked_model_artifact_acquisition_authorization()

    assert authorization["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "authorizationGrantsAcquisitionAuthority": False,
        "authorizationGrantsExecutionAuthority": False,
    }


def test_model_artifact_acquisition_authorization_hash_is_deterministic():
    first = build_blocked_model_artifact_acquisition_authorization()
    second = build_blocked_model_artifact_acquisition_authorization()

    assert first == second
    assert first["modelArtifactAcquisitionAuthorizationHash"] == (
        model_artifact_acquisition_authorization_hash(first)
    )


def test_model_artifact_acquisition_authorization_rejects_download_authority():
    authorization = build_blocked_model_artifact_acquisition_authorization()
    authorization["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_artifact_acquisition_authorization(authorization)


def test_model_artifact_acquisition_authorization_rejects_unblocked_decision():
    decision = build_blocked_model_artifact_acquisition_decision()
    decision["decision"] = "ALLOW"

    with pytest.raises(ValueError, match="blocked no-artifact"):
        build_blocked_model_artifact_acquisition_authorization(decision)


def test_model_artifact_acquisition_authorization_rejects_hash_tampering():
    authorization = build_blocked_model_artifact_acquisition_authorization()
    authorization["modelArtifactAcquisitionAuthorizationHash"] = (
        "sha256:" + "0" * 64
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_model_artifact_acquisition_authorization(authorization)
