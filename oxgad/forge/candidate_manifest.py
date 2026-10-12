"""Candidate manifest binding for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.forge.candidate_output import (
    candidate_output_hash,
    validate_candidate_output,
)
from oxgad.forge.execution_decision import (
    execution_decision_hash,
    validate_execution_decision,
)
from oxgad.structure.canonical import canonical_sha256


CANDIDATE_MANIFEST_SCHEMA_PATH = Path(
    "schemas/ox-candidate-manifest-1.schema.json"
)


def _load_candidate_manifest_schema() -> dict[str, Any]:
    import json

    return json.loads(
        CANDIDATE_MANIFEST_SCHEMA_PATH.read_text()
    )


def build_candidate_manifest(
    *,
    candidate_output: Mapping[str, Any],
    execution_decision: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a candidate manifest from output and execution decision."""

    validate_candidate_output(
        candidate_output
    )
    validate_execution_decision(
        execution_decision
    )

    if execution_decision["backendInvocationAllowed"] is not False:
        raise ValueError(
            "Candidate manifest requires backend invocation to be false."
        )

    manifest = {
        "manifestVersion": "OX-CANDIDATE-MANIFEST-1",
        "candidateId": candidate_output["candidateId"],
        "state": "CANDIDATE_MANIFEST_PREPARED",
        "links": {
            "candidateOutputHash": candidate_output_hash(
                candidate_output
            ),
            "executionDecisionHash": execution_decision_hash(
                execution_decision
            ),
        },
        "authority": {
            "mediaGenerated": False,
            "candidateIsCanonical": False,
            "manualApprovalRequired": True,
            "backendInvocationAllowed": False,
        },
    }

    validate_candidate_manifest(
        manifest
    )

    return manifest


def validate_candidate_manifest(
    manifest: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate candidate manifest."""

    jsonschema.validate(
        dict(manifest),
        _load_candidate_manifest_schema(),
    )

    return manifest


def candidate_manifest_hash(
    manifest: Mapping[str, Any],
) -> str:
    """Return canonical hash for a candidate manifest."""

    return canonical_sha256(
        manifest
    )
