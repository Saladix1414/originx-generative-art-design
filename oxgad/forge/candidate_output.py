"""Candidate output contract helpers for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.structure.canonical import canonical_sha256


CANDIDATE_OUTPUT_SCHEMA_PATH = Path(
    "schemas/ox-candidate-output-1.schema.json"
)


def _load_candidate_schema() -> dict[str, Any]:
    import json

    return json.loads(
        CANDIDATE_OUTPUT_SCHEMA_PATH.read_text()
    )


def build_unapproved_candidate_output(
    *,
    candidate_id: str,
    media_path: str,
    render_plan_hash: str,
    execution_decision_hash: str,
    model_binding_hash: str | None,
) -> dict[str, Any]:
    """Build a schema-valid unapproved candidate output record."""

    candidate = {
        "candidateVersion": "OX-CANDIDATE-OUTPUT-1",
        "candidateId": candidate_id,
        "state": "CANDIDATE_UNAPPROVED",
        "source": {
            "renderPlanHash": render_plan_hash,
            "executionDecisionHash": execution_decision_hash,
            "modelBindingHash": model_binding_hash,
        },
        "media": {
            "path": media_path,
            "mediaHash": None,
            "mimeType": None,
            "width": None,
            "height": None,
        },
        "quality": {
            "qualityGateStatus": "NOT_REVIEWED",
            "canonicalPromotionAllowed": False,
        },
        "authority": {
            "candidateIsCanonical": False,
            "manualApprovalRequired": True,
            "aiOutputIsCanonical": False,
        },
    }

    validate_candidate_output(
        candidate
    )

    return candidate


def validate_candidate_output(
    candidate: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate a candidate output record."""

    jsonschema.validate(
        dict(candidate),
        _load_candidate_schema(),
    )

    return candidate


def candidate_output_hash(
    candidate: Mapping[str, Any],
) -> str:
    """Return canonical hash for a candidate output record."""

    return canonical_sha256(
        candidate
    )
