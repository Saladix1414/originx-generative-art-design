"""Candidate dry-run builder for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from oxgad.forge.candidate_manifest import (
    build_candidate_manifest,
    candidate_manifest_hash,
)
from oxgad.forge.candidate_output import (
    build_unapproved_candidate_output,
    candidate_output_hash,
)
from oxgad.forge.candidate_provenance import (
    build_candidate_provenance_hook,
    candidate_provenance_hook_hash,
)
from oxgad.forge.execution_decision import (
    build_execution_decision,
    execution_decision_hash,
)
from oxgad.structure.canonical import canonical_sha256


def build_candidate_dry_run(
    *,
    candidate_id: str,
    media_path: str,
    render_plan_hash: str,
    forge_contract: Mapping[str, Any],
    model_binding_hash: str | None = None,
) -> dict[str, Any]:
    """Build a complete prepare-only candidate dry run."""

    decision = build_execution_decision(
        forge_contract
    )
    decision_hash = execution_decision_hash(
        decision
    )

    candidate_output = build_unapproved_candidate_output(
        candidate_id=candidate_id,
        media_path=media_path,
        render_plan_hash=render_plan_hash,
        execution_decision_hash=decision_hash,
        model_binding_hash=model_binding_hash,
    )

    candidate_manifest = build_candidate_manifest(
        candidate_output=candidate_output,
        execution_decision=decision,
    )

    provenance_hook = build_candidate_provenance_hook(
        candidate_output=candidate_output,
        candidate_manifest=candidate_manifest,
        execution_decision=decision,
    )

    dry_run = {
        "dryRunVersion": "OX-CANDIDATE-DRY-RUN-1",
        "candidateId": candidate_id,
        "state": "PREPARE_ONLY",
        "executionDecision": decision,
        "candidateOutput": candidate_output,
        "candidateManifest": candidate_manifest,
        "candidateProvenanceHook": provenance_hook,
        "hashes": {
            "executionDecisionHash": decision_hash,
            "candidateOutputHash": candidate_output_hash(
                candidate_output
            ),
            "candidateManifestHash": candidate_manifest_hash(
                candidate_manifest
            ),
            "candidateProvenanceHookHash": candidate_provenance_hook_hash(
                provenance_hook
            ),
        },
        "authority": {
            "backendInvocationAllowed": False,
            "mediaGenerated": False,
            "candidateIsCanonical": False,
            "manualApprovalRequired": True,
            "aiOutputIsCanonical": False,
        },
    }

    return dry_run


def candidate_dry_run_hash(
    dry_run: Mapping[str, Any],
) -> str:
    """Return canonical hash for a candidate dry run."""

    return canonical_sha256(
        dry_run
    )
