"""Candidate provenance hook for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.forge.candidate_manifest import (
    candidate_manifest_hash,
    validate_candidate_manifest,
)
from oxgad.forge.candidate_output import (
    candidate_output_hash,
    validate_candidate_output,
)
from oxgad.forge.execution_decision import (
    execution_decision_hash,
    validate_execution_decision,
)
from oxgad.structure.canonical import canonical_sha256


CANDIDATE_PROVENANCE_SCHEMA_PATH = Path(
    "schemas/ox-candidate-provenance-hook-1.schema.json"
)


def _load_candidate_provenance_schema() -> dict[str, Any]:
    import json

    return json.loads(
        CANDIDATE_PROVENANCE_SCHEMA_PATH.read_text()
    )


def build_candidate_provenance_hook(
    *,
    candidate_output: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    execution_decision: Mapping[str, Any],
) -> dict[str, Any]:
    """Build provenance hook for a prepared candidate."""

    validate_candidate_output(
        candidate_output
    )
    validate_candidate_manifest(
        candidate_manifest
    )
    validate_execution_decision(
        execution_decision
    )

    if candidate_output["candidateId"] != candidate_manifest["candidateId"]:
        raise ValueError(
            "Candidate id mismatch."
        )

    if execution_decision["backendInvocationAllowed"] is not False:
        raise ValueError(
            "Candidate provenance requires backend invocation to be false."
        )

    hook = {
        "hookVersion": "OX-CANDIDATE-PROVENANCE-HOOK-1",
        "candidateId": candidate_output["candidateId"],
        "state": "PROVENANCE_PREPARED",
        "links": {
            "candidateOutputHash": candidate_output_hash(
                candidate_output
            ),
            "candidateManifestHash": candidate_manifest_hash(
                candidate_manifest
            ),
            "executionDecisionHash": execution_decision_hash(
                execution_decision
            ),
        },
        "media": {
            "mediaGenerated": False,
            "mediaHash": None,
            "path": candidate_output["media"]["path"],
        },
        "authority": {
            "candidateIsCanonical": False,
            "manualApprovalRequired": True,
            "backendInvocationAllowed": False,
            "aiOutputIsCanonical": False,
        },
    }

    validate_candidate_provenance_hook(
        hook
    )

    return hook


def validate_candidate_provenance_hook(
    hook: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate candidate provenance hook."""

    jsonschema.validate(
        dict(hook),
        _load_candidate_provenance_schema(),
    )

    return hook


def candidate_provenance_hook_hash(
    hook: Mapping[str, Any],
) -> str:
    """Return canonical hash for candidate provenance hook."""

    return canonical_sha256(
        hook
    )
