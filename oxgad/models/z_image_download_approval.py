from __future__ import annotations

from typing import Any

Z_IMAGE_DOWNLOAD_APPROVAL_VERSION = (
    "OX-Z-IMAGE-DOWNLOAD-APPROVAL-1"
)

Z_IMAGE_APPROVAL_PHRASE = (
    "I APPROVE OX-MODEL-001 Z-IMAGE ARTIFACT DOWNLOAD"
)


def build_z_image_download_approval_request() -> dict[str, Any]:
    return {
        "approvalVersion": Z_IMAGE_DOWNLOAD_APPROVAL_VERSION,
        "modelId": "OX-MODEL-001",
        "state": "AWAITING_EXPLICIT_APPROVAL",
        "requiredPhrase": Z_IMAGE_APPROVAL_PHRASE,
        "approval": {
            "explicitApprovalPresent": False,
            "phraseAccepted": False,
            "approvalGrantsExecutionAuthority": False,
            "approvalGrantsCanonicalizationAuthority": False,
        },
        "scope": {
            "artifactCount": 3,
            "expectedSizeBytes": 6348318966,
            "downloadOnly": True,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
    }


def accept_z_image_download_approval(
    phrase: str,
) -> dict[str, Any]:
    value = build_z_image_download_approval_request()

    if phrase != Z_IMAGE_APPROVAL_PHRASE:
        raise ValueError("explicit approval phrase mismatch")

    value["state"] = "EXPLICIT_DOWNLOAD_APPROVAL_RECORDED"
    value["approval"]["explicitApprovalPresent"] = True
    value["approval"]["phraseAccepted"] = True
    value["governance"]["downloadAllowed"] = True

    return value
