from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.models.acquisition import build_first_local_model_plan


MODEL_DOWNLOAD_AUTHORIZATION_DRAFT_SCHEMA_PATH = Path(
    "schemas/ox-model-download-authorization-draft-1.schema.json"
)


def build_model_download_authorization_draft() -> dict[str, Any]:
    """Build a non-authorizing draft for the selected model download path."""
    plan = build_first_local_model_plan()

    draft = {
        "authorizationDraftVersion": "OX-MODEL-DOWNLOAD-AUTHORIZATION-DRAFT-1",
        "state": "DRAFT_NOT_APPROVED",
        "selectedPath": "AUTHORIZED_DOWNLOAD",
        "approval": {
            "manualApprovalRequired": True,
            "manualApprovalPresent": False,
            "approvalTokenRequired": True,
            "approvalToken": None,
        },
        "targetModel": {
            "modelId": plan["model"]["modelId"],
            "family": plan["model"]["family"],
            "repository": plan["source"]["repository"],
            "filename": plan["source"]["filename"],
            "expectedSizeBytes": plan["artifact"]["expectedSizeBytes"],
            "expectedSha256": plan["artifact"]["expectedSha256"],
        },
        "requirements": {
            "licenseReviewRequired": True,
            "storageCheckRequired": True,
            "hashVerificationRequired": True,
            "runtimeCompatibilityRequired": True,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "draftGrantsAuthority": False,
        },
    }

    return validate_model_download_authorization_draft(draft)


def validate_model_download_authorization_draft(
    draft: dict[str, Any],
) -> dict[str, Any]:
    """Validate a model download authorization draft."""
    schema = json.loads(
        MODEL_DOWNLOAD_AUTHORIZATION_DRAFT_SCHEMA_PATH.read_text()
    )
    jsonschema.validate(draft, schema)
    return draft
