from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-review-pack-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase13"


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be present")
    return value


def build_review_pack(
    *,
    review_id: str,
    provenance_manifest: dict[str, Any],
    quality_report: dict[str, Any],
    promotion_decision: dict[str, Any],
    ledger: dict[str, Any],
    output_manifest: dict[str, Any],
) -> dict[str, Any]:
    canonical_id = _require_text("canonical_id", output_manifest.get("canonical_id"))
    candidate_id = _require_text("candidate_id", output_manifest.get("candidate_id"))

    ledger_index = output_manifest.get("evidence", {}).get("ledger_index")
    if not isinstance(ledger_index, int) or ledger_index < 0:
        raise ValueError("ledger_index must be present")

    entries = ledger.get("entries", [])
    if not isinstance(entries, list) or ledger_index >= len(entries):
        raise ValueError("ledger must contain output manifest index")

    quality_required_passed = (
        quality_report.get("summary", {}).get("required_passed") is True
    )
    promotion_value = promotion_decision.get("decision")

    ready_for_review = (
        quality_required_passed
        and promotion_value == "promoted"
        and output_manifest.get("evidence", {}).get("promotion_decision") == "promoted"
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "review_id": _require_text("review_id", review_id),
        "canonical_id": canonical_id,
        "candidate_id": candidate_id,
        "documents": {
            "provenance_schema_version": provenance_manifest.get("schema_version"),
            "quality_schema_version": quality_report.get("schema_version"),
            "promotion_schema_version": promotion_decision.get("schema_version"),
            "ledger_schema_version": ledger.get("schema_version"),
            "output_manifest_schema_version": output_manifest.get("schema_version"),
        },
        "summary": {
            "ready_for_review": ready_for_review,
            "promotion_decision": promotion_value,
            "quality_required_passed": quality_required_passed,
            "ledger_index": ledger_index,
        },
    }
