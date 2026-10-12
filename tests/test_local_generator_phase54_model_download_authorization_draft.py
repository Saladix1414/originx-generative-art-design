import jsonschema
import pytest

from oxgad.models.download_authorization import (
    build_model_download_authorization_draft,
    validate_model_download_authorization_draft,
)


def test_model_download_authorization_draft_is_not_approved():
    draft = build_model_download_authorization_draft()

    assert draft["authorizationDraftVersion"] == (
        "OX-MODEL-DOWNLOAD-AUTHORIZATION-DRAFT-1"
    )
    assert draft["state"] == "DRAFT_NOT_APPROVED"
    assert draft["selectedPath"] == "AUTHORIZED_DOWNLOAD"


def test_model_download_authorization_draft_preserves_target_model():
    draft = build_model_download_authorization_draft()

    assert draft["targetModel"]["modelId"] == "originx.sd15.emaonly"
    assert draft["targetModel"]["family"] == "stable-diffusion-1"
    assert draft["targetModel"]["filename"] == (
        "v1-5-pruned-emaonly.safetensors"
    )
    assert draft["targetModel"]["expectedSizeBytes"] == 4265146304


def test_model_download_authorization_draft_requires_manual_approval():
    draft = build_model_download_authorization_draft()

    assert draft["approval"]["manualApprovalRequired"] is True
    assert draft["approval"]["manualApprovalPresent"] is False
    assert draft["approval"]["approvalTokenRequired"] is True
    assert draft["approval"]["approvalToken"] is None


def test_model_download_authorization_draft_does_not_grant_authority():
    draft = build_model_download_authorization_draft()
    governance = draft["governance"]

    assert governance["downloadAllowed"] is False
    assert governance["installationAllowed"] is False
    assert governance["executionAllowed"] is False
    assert governance["mediaGenerationAllowed"] is False
    assert governance["draftGrantsAuthority"] is False


def test_model_download_authorization_draft_rejects_download_authority():
    draft = build_model_download_authorization_draft()
    draft["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_download_authorization_draft(draft)
