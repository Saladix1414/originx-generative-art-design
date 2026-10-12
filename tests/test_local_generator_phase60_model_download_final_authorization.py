import jsonschema
import pytest

from oxgad.models.download_final_authorization import (
    build_blocked_model_download_final_authorization,
    validate_model_download_final_authorization,
)


def test_model_download_final_authorization_is_blocked_pending_checks():
    authorization = build_blocked_model_download_final_authorization()

    assert authorization["finalAuthorizationVersion"] == (
        "OX-MODEL-DOWNLOAD-FINAL-AUTHORIZATION-1"
    )
    assert authorization["state"] == "BLOCKED_PENDING_REQUIRED_CHECKS"
    assert authorization["selectedPath"] == "AUTHORIZED_DOWNLOAD"


def test_model_download_final_authorization_records_accepted_approval_token():
    authorization = build_blocked_model_download_final_authorization()

    assert authorization["approvalState"]["approvalTokenPresent"] is True
    assert authorization["approvalState"]["manualApprovalPresent"] is True
    assert authorization["approvalState"]["approvalPhraseAccepted"] is True


def test_model_download_final_authorization_blocks_until_required_checks_complete():
    authorization = build_blocked_model_download_final_authorization()
    checks = authorization["blockingChecks"]

    assert checks["licenseReviewCompleted"] is False
    assert checks["storageCheckCompleted"] is False
    assert checks["runtimeCompatibilityChecked"] is False
    assert checks["hashVerificationPlanned"] is True


def test_model_download_final_authorization_does_not_grant_download():
    authorization = build_blocked_model_download_final_authorization()
    governance = authorization["governance"]

    assert governance["downloadAllowed"] is False
    assert governance["installationAllowed"] is False
    assert governance["executionAllowed"] is False
    assert governance["mediaGenerationAllowed"] is False
    assert governance["finalGateGrantsAuthority"] is False


def test_model_download_final_authorization_rejects_download_authority():
    authorization = build_blocked_model_download_final_authorization()
    authorization["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_download_final_authorization(authorization)
