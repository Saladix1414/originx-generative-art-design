import pytest

from oxgad.models.z_image_download_approval import (
    Z_IMAGE_APPROVAL_PHRASE,
    accept_z_image_download_approval,
    build_z_image_download_approval_request,
)


def test_z_image_download_approval_is_initially_blocked():
    value = build_z_image_download_approval_request()

    assert value["state"] == "AWAITING_EXPLICIT_APPROVAL"
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["canonicalizationAllowed"] is False


def test_incorrect_phrase_is_rejected():
    with pytest.raises(ValueError):
        accept_z_image_download_approval("yes")


def test_exact_phrase_authorizes_download_only():
    value = accept_z_image_download_approval(
        Z_IMAGE_APPROVAL_PHRASE
    )

    assert value["governance"]["downloadAllowed"] is True
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["canonicalizationAllowed"] is False
    assert value["scope"]["downloadOnly"] is True
