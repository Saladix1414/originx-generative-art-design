from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-project-readiness-summary-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase20"


def summarize_project_readiness(
    *,
    review_pack: dict[str, Any],
    release_readiness: dict[str, Any],
    release_ledger: dict[str, Any],
    export_audit_ledger: dict[str, Any],
) -> dict[str, Any]:
    review_ready = review_pack.get("summary", {}).get("ready_for_review") is True
    release_ready = release_readiness.get("status") == "ready"

    release_id = release_readiness.get("release_id")
    release_recorded = any(
        isinstance(entry, dict)
        and entry.get("release_id") == release_id
        and entry.get("status") == "ready"
        for entry in release_ledger.get("entries", [])
        if isinstance(release_ledger.get("entries", []), list)
    )

    export_recorded = any(
        isinstance(entry, dict)
        and entry.get("status") == "exported"
        for entry in export_audit_ledger.get("entries", [])
        if isinstance(export_audit_ledger.get("entries", []), list)
    )

    status = (
        "ready"
        if review_ready and release_ready and release_recorded and export_recorded
        else "blocked"
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "status": status,
        "checks": {
            "review_ready": review_ready,
            "release_ready": release_ready,
            "release_recorded": release_recorded,
            "export_recorded": export_recorded,
        },
    }
