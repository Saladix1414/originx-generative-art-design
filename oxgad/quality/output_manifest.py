from __future__ import annotations

import re
from typing import Any

_SCHEMA_VERSION = "ox-canonical-output-manifest-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase12"
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be present")
    return value


def _require_sha256(name: str, value: object) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase sha256 hex digest")
    return value


def build_canonical_output_manifest(
    *,
    canonical_id: str,
    candidate_id: str,
    promotion_decision: dict[str, Any],
    provenance_manifest: dict[str, Any],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    if promotion_decision.get("decision") != "promoted":
        raise ValueError("promotion decision must be promoted")

    output = provenance_manifest.get("output", {})
    integrity = provenance_manifest.get("integrity", {})

    ledger_entries = ledger.get("entries", [])
    if not isinstance(ledger_entries, list):
        raise ValueError("ledger entries must be a list")

    matching_entries = [
        entry
        for entry in ledger_entries
        if isinstance(entry, dict)
        and entry.get("canonical_id") == canonical_id
        and entry.get("candidate_id") == candidate_id
        and entry.get("decision") == "promoted"
    ]

    if not matching_entries:
        raise ValueError("ledger must contain promoted canonical entry")

    ledger_entry = matching_entries[-1]

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "canonical_id": _require_text("canonical_id", canonical_id),
        "candidate_id": _require_text("candidate_id", candidate_id),
        "artifact": {
            "artifact_id": _require_text("artifact_id", output.get("artifact_id")),
            "sha256": _require_sha256("artifact.sha256", output.get("sha256")),
        },
        "evidence": {
            "provenance_manifest_sha256": _require_sha256(
                "provenance_manifest_sha256",
                integrity.get("manifest_sha256"),
            ),
            "promotion_decision": "promoted",
            "ledger_index": ledger_entry["index"],
        },
    }
