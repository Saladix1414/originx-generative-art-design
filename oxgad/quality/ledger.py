from __future__ import annotations

import re
from typing import Any

_SCHEMA_VERSION = "ox-canonical-ledger-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase11"
_PROMOTION_SCHEMA = "ox-canonical-promotion-1"
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def empty_canonical_ledger() -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [],
    }


def append_promotion_decision(
    ledger: dict[str, Any],
    promotion_decision: dict[str, Any],
) -> dict[str, Any]:
    entries = ledger.get("entries")

    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")

    canonical_id = promotion_decision.get("canonical_id")
    candidate_id = promotion_decision.get("candidate_id")
    decision = promotion_decision.get("decision")
    evidence = promotion_decision.get("evidence", {})
    provenance_sha = evidence.get("provenance_manifest_sha256")

    if not isinstance(canonical_id, str) or not canonical_id.strip():
        raise ValueError("canonical_id must be present")

    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be present")

    if decision not in {"promoted", "blocked"}:
        raise ValueError("decision must be promoted or blocked")

    if not isinstance(provenance_sha, str) or not _SHA256_RE.fullmatch(provenance_sha):
        raise ValueError("provenance_manifest_sha256 must be valid")

    next_ledger = {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [
            *entries,
            {
                "index": len(entries),
                "canonical_id": canonical_id,
                "candidate_id": candidate_id,
                "decision": decision,
                "promotion_schema_version": _PROMOTION_SCHEMA,
                "provenance_manifest_sha256": provenance_sha,
            },
        ],
    }

    return next_ledger


def canonical_ids(ledger: dict[str, Any]) -> list[str]:
    entries = ledger.get("entries", [])

    if not isinstance(entries, list):
        return []

    return [
        entry["canonical_id"]
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("decision") == "promoted"
        and isinstance(entry.get("canonical_id"), str)
    ]
