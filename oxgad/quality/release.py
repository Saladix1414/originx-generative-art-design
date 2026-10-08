from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-release-readiness-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase14"

_REQUIRED_DOCUMENT_SCHEMAS = {
    "provenance_schema_version": "ox-provenance-manifest-1",
    "quality_schema_version": "ox-quality-gate-report-1",
    "promotion_schema_version": "ox-canonical-promotion-1",
    "ledger_schema_version": "ox-canonical-ledger-1",
    "output_manifest_schema_version": "ox-canonical-output-manifest-1",
}


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be present")
    return value


def evaluate_release_readiness(
    *,
    release_id: str,
    review_pack: dict[str, Any],
    release_authority_granted: bool,
) -> dict[str, Any]:
    documents = review_pack.get("documents", {})
    summary = review_pack.get("summary", {})

    schema_chain_complete = all(
        documents.get(key) == expected
        for key, expected in _REQUIRED_DOCUMENT_SCHEMAS.items()
    )

    review_ready = summary.get("ready_for_review") is True
    status = (
        "ready"
        if review_ready and schema_chain_complete and release_authority_granted
        else "blocked"
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "release_id": _require_text("release_id", release_id),
        "review_id": _require_text("review_id", review_pack.get("review_id")),
        "canonical_id": _require_text("canonical_id", review_pack.get("canonical_id")),
        "status": status,
        "checks": {
            "review_ready": review_ready,
            "schema_chain_complete": schema_chain_complete,
            "release_authority_granted": bool(release_authority_granted),
        },
    }
