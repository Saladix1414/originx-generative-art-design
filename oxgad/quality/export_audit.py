from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-export-audit-ledger-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase19"
_EXPORT_RESULT_SCHEMA = "ox-local-export-result-1"


def empty_export_audit_ledger() -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [],
    }


def append_export_result(
    ledger: dict[str, Any],
    export_result: dict[str, Any],
) -> dict[str, Any]:
    entries = ledger.get("entries")

    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")

    if export_result.get("schema_version") != _EXPORT_RESULT_SCHEMA:
        raise ValueError("export result schema version is invalid")

    export_id = export_result.get("export_id")
    status = export_result.get("status")
    written = export_result.get("written", {})

    if not isinstance(export_id, str) or not export_id.strip():
        raise ValueError("export_id must be present")

    if status not in {"exported", "blocked"}:
        raise ValueError("status must be exported or blocked")

    manifest_path = written.get("manifest_path")
    artifact_path = written.get("artifact_path")

    if not isinstance(manifest_path, str):
        raise ValueError("manifest_path must be present")

    if not isinstance(artifact_path, str):
        raise ValueError("artifact_path must be present")

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "entries": [
            *entries,
            {
                "index": len(entries),
                "export_id": export_id,
                "status": status,
                "manifest_path": manifest_path,
                "artifact_path": artifact_path,
                "export_result_schema_version": _EXPORT_RESULT_SCHEMA,
            },
        ],
    }


def exported_ids(ledger: dict[str, Any]) -> list[str]:
    entries = ledger.get("entries", [])

    if not isinstance(entries, list):
        return []

    return [
        entry["export_id"]
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("status") == "exported"
        and isinstance(entry.get("export_id"), str)
    ]
