from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import shutil
from typing import Any

_SCHEMA_VERSION = "ox-local-export-result-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase18"


def _canonical_relative_path(value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("export path must be present")

    path = PurePosixPath(value)

    if path.is_absolute() or ".." in path.parts:
        raise ValueError("export path must be relative and canonical")

    if len(path.parts) < 3 or path.parts[0] != "output" or path.parts[1] != "canonical":
        raise ValueError("export path must stay under output/canonical")

    return Path(*path.parts)


def execute_local_export(
    *,
    export_plan: dict[str, Any],
    dry_run: dict[str, Any],
    canonical_output_manifest: dict[str, Any],
    artifact_source_path: str,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    if dry_run.get("status") != "ready":
        return {
            "schema_version": _SCHEMA_VERSION,
            "project": _PROJECT,
            "phase": _PHASE,
            "export_id": export_plan.get("export_id", ""),
            "status": "blocked",
            "written": {
                "manifest_path": export_plan.get("planned_paths", {}).get("manifest_path", ""),
                "artifact_path": export_plan.get("planned_paths", {}).get("artifact_path", ""),
            },
        }

    planned_paths = export_plan.get("planned_paths", {})
    manifest_rel = _canonical_relative_path(planned_paths.get("manifest_path"))
    artifact_rel = _canonical_relative_path(planned_paths.get("artifact_path"))

    root = Path(repo_root)
    source = Path(artifact_source_path)

    if not source.is_file():
        raise ValueError("artifact source must exist")

    manifest_path = root / manifest_rel
    artifact_path = root / artifact_rel

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_path.write_text(
        json.dumps(canonical_output_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(source, artifact_path)

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "export_id": export_plan.get("export_id", ""),
        "status": "exported",
        "written": {
            "manifest_path": str(manifest_rel).replace("\\", "/"),
            "artifact_path": str(artifact_rel).replace("\\", "/"),
        },
    }
