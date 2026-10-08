from __future__ import annotations

from typing import Any

_SCHEMA_VERSION = "ox-local-export-plan-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase16"


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be present")
    return value


def _safe_segment(name: str, value: str) -> str:
    value = _require_text(name, value)

    if "/" in value or "\\" in value or value in {".", ".."}:
        raise ValueError(f"{name} must be a safe path segment")

    return value


def build_local_export_plan(
    *,
    export_id: str,
    release_readiness: dict[str, Any],
    artifact_filename: str,
) -> dict[str, Any]:
    release_id = _require_text("release_id", release_readiness.get("release_id"))
    canonical_id = _safe_segment("canonical_id", release_readiness.get("canonical_id"))
    artifact_filename = _safe_segment("artifact_filename", artifact_filename)

    status = (
        "planned"
        if release_readiness.get("status") == "ready"
        else "blocked"
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "export_id": _require_text("export_id", export_id),
        "release_id": release_id,
        "canonical_id": canonical_id,
        "status": status,
        "planned_paths": {
            "manifest_path": f"output/canonical/{canonical_id}/manifest.json",
            "artifact_path": f"output/canonical/{canonical_id}/{artifact_filename}",
        },
    }
