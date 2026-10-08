from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

_SCHEMA_VERSION = "ox-local-export-dry-run-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase17"


def _is_canonical_output_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False

    path = PurePosixPath(value)

    if path.is_absolute() or ".." in path.parts:
        return False

    return len(path.parts) >= 3 and path.parts[0] == "output" and path.parts[1] == "canonical"


def evaluate_local_export_dry_run(
    *,
    export_plan: dict[str, Any],
    artifact_source_path: str | None,
) -> dict[str, Any]:
    planned_paths = export_plan.get("planned_paths", {})

    plan_is_planned = export_plan.get("status") == "planned"
    artifact_source_present = isinstance(artifact_source_path, str) and bool(
        artifact_source_path.strip()
    )
    paths_are_canonical = (
        _is_canonical_output_path(planned_paths.get("manifest_path"))
        and _is_canonical_output_path(planned_paths.get("artifact_path"))
    )

    status = (
        "ready"
        if plan_is_planned and artifact_source_present and paths_are_canonical
        else "blocked"
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "export_id": export_plan.get("export_id", ""),
        "status": status,
        "checks": {
            "plan_is_planned": plan_is_planned,
            "artifact_source_present": artifact_source_present,
            "paths_are_canonical": paths_are_canonical,
        },
    }
