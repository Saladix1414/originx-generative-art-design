from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.models.download_approval import build_model_download_approval_token


MODEL_DOWNLOAD_FINAL_AUTHORIZATION_SCHEMA_PATH = Path(
    "schemas/ox-model-download-final-authorization-1.schema.json"
)


def build_blocked_model_download_final_authorization() -> dict[str, Any]:
    """Build the final download authorization gate in its blocked state."""
    token = build_model_download_approval_token()

    authorization = {
        "finalAuthorizationVersion": "OX-MODEL-DOWNLOAD-FINAL-AUTHORIZATION-1",
        "state": "BLOCKED_PENDING_REQUIRED_CHECKS",
        "selectedPath": token["selectedPath"],
        "approvalState": {
            "approvalTokenPresent": True,
            "manualApprovalPresent": token["approval"]["manualApprovalPresent"],
            "approvalPhraseAccepted": True,
        },
        "blockingChecks": {
            "licenseReviewCompleted": token["checks"]["licenseReviewCompleted"],
            "storageCheckCompleted": token["checks"]["storageCheckCompleted"],
            "runtimeCompatibilityChecked": token["checks"]["runtimeCompatibilityChecked"],
            "hashVerificationPlanned": token["checks"]["hashVerificationPlanned"],
        },
        "targetModel": token["targetModel"],
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "finalGateGrantsAuthority": False,
        },
    }

    return validate_model_download_final_authorization(authorization)


def validate_model_download_final_authorization(
    authorization: dict[str, Any],
) -> dict[str, Any]:
    """Validate a final model download authorization gate payload."""
    schema = json.loads(
        MODEL_DOWNLOAD_FINAL_AUTHORIZATION_SCHEMA_PATH.read_text()
    )
    jsonschema.validate(authorization, schema)
    return authorization
