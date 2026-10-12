from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.models.acquisition import build_first_local_model_plan


MODEL_DOWNLOAD_APPROVAL_TOKEN_SCHEMA_PATH = Path(
    "schemas/ox-model-download-approval-token-1.schema.json"
)


APPROVAL_PHRASE = "I APPROVE ORIGINX FIRST LOCAL MODEL DOWNLOAD"


def build_model_download_approval_token() -> dict[str, Any]:
    """Build a declared approval token that still does not grant authority."""
    plan = build_first_local_model_plan()

    token = {
        "approvalTokenVersion": "OX-MODEL-DOWNLOAD-APPROVAL-TOKEN-1",
        "state": "APPROVAL_TOKEN_DECLARED",
        "selectedPath": "AUTHORIZED_DOWNLOAD",
        "approval": {
            "manualApprovalPresent": True,
            "approvalPhrase": APPROVAL_PHRASE,
            "approvalGrantsDownloadAuthority": False,
        },
        "targetModel": {
            "modelId": plan["model"]["modelId"],
            "repository": plan["source"]["repository"],
            "filename": plan["source"]["filename"],
            "expectedSizeBytes": plan["artifact"]["expectedSizeBytes"],
            "expectedSha256": plan["artifact"]["expectedSha256"],
        },
        "checks": {
            "licenseReviewCompleted": False,
            "storageCheckCompleted": False,
            "runtimeCompatibilityChecked": False,
            "hashVerificationPlanned": True,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "tokenAloneGrantsAuthority": False,
        },
    }

    return validate_model_download_approval_token(token)


def validate_model_download_approval_token(
    token: dict[str, Any],
) -> dict[str, Any]:
    """Validate a model download approval token."""
    schema = json.loads(
        MODEL_DOWNLOAD_APPROVAL_TOKEN_SCHEMA_PATH.read_text()
    )
    jsonschema.validate(token, schema)
    return token
