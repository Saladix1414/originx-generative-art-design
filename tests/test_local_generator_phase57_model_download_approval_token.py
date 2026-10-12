import jsonschema
import pytest

from oxgad.models.download_approval import (
    APPROVAL_PHRASE,
    build_model_download_approval_token,
    validate_model_download_approval_token,
)


def test_model_download_approval_token_records_manual_phrase():
    token = build_model_download_approval_token()

    assert token["approvalTokenVersion"] == "OX-MODEL-DOWNLOAD-APPROVAL-TOKEN-1"
    assert token["state"] == "APPROVAL_TOKEN_DECLARED"
    assert token["selectedPath"] == "AUTHORIZED_DOWNLOAD"
    assert token["approval"]["manualApprovalPresent"] is True
    assert token["approval"]["approvalPhrase"] == APPROVAL_PHRASE


def test_model_download_approval_token_alone_does_not_grant_authority():
    token = build_model_download_approval_token()
    governance = token["governance"]

    assert token["approval"]["approvalGrantsDownloadAuthority"] is False
    assert governance["downloadAllowed"] is False
    assert governance["installationAllowed"] is False
    assert governance["executionAllowed"] is False
    assert governance["mediaGenerationAllowed"] is False
    assert governance["tokenAloneGrantsAuthority"] is False


def test_model_download_approval_token_preserves_target_model():
    token = build_model_download_approval_token()

    assert token["targetModel"]["modelId"] == "originx.sd15.emaonly"
    assert token["targetModel"]["filename"] == "v1-5-pruned-emaonly.safetensors"
    assert token["targetModel"]["expectedSizeBytes"] == 4265146304


def test_model_download_approval_token_rejects_download_authority():
    token = build_model_download_approval_token()
    token["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_download_approval_token(token)


def test_model_download_approval_token_rejects_wrong_phrase():
    token = build_model_download_approval_token()
    token["approval"]["approvalPhrase"] = "approve"

    with pytest.raises(jsonschema.ValidationError):
        validate_model_download_approval_token(token)
