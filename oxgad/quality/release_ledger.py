from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-release-ledger-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase15"
_RELEASE_SCHEMA = "ox-release-readiness-1"


def empty_release_ledger() -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [],
    }


def append_release_readiness(
    ledger: dict[str, Any],
    release_readiness: dict[str, Any],
) -> dict[str, Any]:
    entries = ledger.get("entries")

    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")

    if release_readiness.get("schema_version") != _RELEASE_SCHEMA:
        raise ValueError("release readiness schema version is invalid")

    release_id = release_readiness.get("release_id")
    review_id = release_readiness.get("review_id")
    canonical_id = release_readiness.get("canonical_id")
    status = release_readiness.get("status")

    if not isinstance(release_id, str) or not release_id.strip():
        raise ValueError("release_id must be present")

    if not isinstance(review_id, str) or not review_id.strip():
        raise ValueError("review_id must be present")

    if not isinstance(canonical_id, str) or not canonical_id.strip():
        raise ValueError("canonical_id must be present")

    if status not in {"ready", "blocked"}:
        raise ValueError("status must be ready or blocked")

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [
            *entries,
            {
                "index": len(entries),
                "release_id": release_id,
                "review_id": review_id,
                "canonical_id": canonical_id,
                "status": status,
                "release_schema_version": _RELEASE_SCHEMA,
            },
        ],
    }


def ready_release_ids(ledger: dict[str, Any]) -> list[str]:
    entries = ledger.get("entries", [])

    if not isinstance(entries, list):
        return []

    return [
        entry["release_id"]
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("status") == "ready"
        and isinstance(entry.get("release_id"), str)
    ]
