import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.quality import execute_local_export


def _plan():
    return {
        "schema_version": "ox-local-export-plan-1",
        "project": "originx-generative-art-design",
        "phase": "phase16",
        "export_id": "export-0001",
        "release_id": "release-0001",
        "canonical_id": "canonical-0001",
        "status": "planned",
        "planned_paths": {
            "manifest_path": "output/canonical/canonical-0001/manifest.json",
            "artifact_path": "output/canonical/canonical-0001/artifact.png",
        },
    }


def _dry_run(status="ready"):
    return {
        "schema_version": "ox-local-export-dry-run-1",
        "project": "originx-generative-art-design",
        "phase": "phase17",
        "export_id": "export-0001",
        "status": status,
        "checks": {
            "plan_is_planned": status == "ready",
            "artifact_source_present": status == "ready",
            "paths_are_canonical": status == "ready",
        },
    }


def _manifest():
    return {
        "schema_version": "ox-canonical-output-manifest-1",
        "project": "originx-generative-art-design",
        "phase": "phase12",
        "canonical_id": "canonical-0001",
        "candidate_id": "candidate-0001",
        "artifact": {
            "artifact_id": "candidate-0001",
            "sha256": "a" * 64,
        },
        "evidence": {
            "provenance_manifest_sha256": "b" * 64,
            "promotion_decision": "promoted",
            "ledger_index": 0,
        },
    }


def test_local_export_executor_matches_schema_and_writes_files(tmp_path):
    source = tmp_path / "source.png"
    source.write_bytes(b"fake-image")

    result = execute_local_export(
        export_plan=_plan(),
        dry_run=_dry_run(),
        canonical_output_manifest=_manifest(),
        artifact_source_path=str(source),
        repo_root=tmp_path,
    )

    schema = json.loads(Path("schemas/ox-local-export-result-1.schema.json").read_text())
    jsonschema.validate(result, schema)

    assert result["schema_version"] == "ox-local-export-result-1"
    assert result["status"] == "exported"
    assert (tmp_path / "output/canonical/canonical-0001/manifest.json").is_file()
    assert (tmp_path / "output/canonical/canonical-0001/artifact.png").read_bytes() == b"fake-image"


def test_local_export_executor_blocks_when_dry_run_not_ready(tmp_path):
    source = tmp_path / "source.png"
    source.write_bytes(b"fake-image")

    result = execute_local_export(
        export_plan=_plan(),
        dry_run=_dry_run(status="blocked"),
        canonical_output_manifest=_manifest(),
        artifact_source_path=str(source),
        repo_root=tmp_path,
    )

    assert result["status"] == "blocked"
    assert not (tmp_path / "output").exists()


def test_local_export_executor_rejects_path_escape(tmp_path):
    source = tmp_path / "source.png"
    source.write_bytes(b"fake-image")
    plan = _plan()
    plan["planned_paths"]["artifact_path"] = "../escape.png"

    with pytest.raises(ValueError, match="canonical"):
        execute_local_export(
            export_plan=plan,
            dry_run=_dry_run(),
            canonical_output_manifest=_manifest(),
            artifact_source_path=str(source),
            repo_root=tmp_path,
        )


def test_local_export_executor_requires_existing_source(tmp_path):
    with pytest.raises(ValueError, match="source"):
        execute_local_export(
            export_plan=_plan(),
            dry_run=_dry_run(),
            canonical_output_manifest=_manifest(),
            artifact_source_path=str(tmp_path / "missing.png"),
            repo_root=tmp_path,
        )
