from __future__ import annotations

import re
from typing import Any

_SCHEMA_VERSION = "ox-canonical-promotion-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase10"
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))


def decide_canonical_promotion(
    *,
    candidate_id: str,
    canonical_id: str,
    quality_report: dict[str, Any],
) -> dict[str, Any]:
    summary = quality_report.get("summary", {})
    required_passed = summary.get("required_passed") is True
    failed_required = summary.get("failed_required", [])

    if not isinstance(failed_required, list):
        failed_required = ["quality-summary-invalid"]

    provenance_sha = quality_report.get("provenance_manifest_sha256")
    has_provenance = _valid_sha256(provenance_sha)
    has_ids = bool(_text(candidate_id).strip()) and bool(_text(canonical_id).strip())

    decision = (
        "promoted"
        if required_passed and has_provenance and has_ids
        else "blocked"
    )

    normalized_failed_required = [
        item
        for item in failed_required
        if isinstance(item, str)
    ]

    if not has_provenance:
        normalized_failed_required.append("provenance-manifest-sha256-invalid")

    if not has_ids:
        normalized_failed_required.append("promotion-identifiers-missing")

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "candidate_id": candidate_id,
        "canonical_id": canonical_id,
        "decision": decision,
        "evidence": {
            "provenance_manifest_sha256": provenance_sha if isinstance(provenance_sha, str) else "",
            "quality_required_passed": required_passed,
            "failed_required": normalized_failed_required,
        },
    }
