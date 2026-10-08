import json
from pathlib import Path

import jsonschema

from oxgad.quality import (
    build_local_export_plan,
    evaluate_local_export_dry_run,
)


def _plan(status="ready"):
    readiness = {
        "schema_version": "ox-release-readiness-1",
        "project": "originx-generative-art-design",
        "phase": "phase14",
        "release_id": "release-0001",
        "review_id": "review-0001",
        "canonical_id": "canonical-0001",
        "status": status,
        "checks": {
            "review_ready": status == "ready",
            "schema_chain_complete": status == "ready",
            "release_authority_granted": status == "ready",
        },
    }

    return build_local_export_plan(
        export_id="export-0001",
        release_readiness=readiness,
        artifact_filename="artifact.png",
    )


def test_local_export_dry_run_matches_schema_when_ready():
    dry_run = evaluate_local_export_dry_run(
        export_plan=_plan(),
        artifact_source_path="output/candidates/candidate-0001/artifact.png",
    )

    schema = json.loads(Path("schemas/ox-local-export-dry-run-1.schema.json").read_text())
    jsonschema.validate(dry_run, schema)

    assert dry_run["schema_version"] == "ox-local-export-dry-run-1"
    assert dry_run["status"] == "ready"
    assert dry_run["checks"]["plan_is_planned"] is True
    assert dry_run["checks"]["artifact_source_present"] is True
    assert dry_run["checks"]["paths_are_canonical"] is True


def test_local_export_dry_run_blocks_missing_source():
    dry_run = evaluate_local_export_dry_run(
        export_plan=_plan(),
        artifact_source_path="",
    )

    assert dry_run["status"] == "blocked"
    assert dry_run["checks"]["artifact_source_present"] is False


def test_local_export_dry_run_blocks_noncanonical_paths():
    plan = _plan()
    plan["planned_paths"]["artifact_path"] = "../escape.png"

    dry_run = evaluate_local_export_dry_run(
        export_plan=plan,
        artifact_source_path="output/candidates/candidate-0001/artifact.png",
    )

    assert dry_run["status"] == "blocked"
    assert dry_run["checks"]["paths_are_canonical"] is False


def test_local_export_dry_run_blocks_blocked_plan():
    dry_run = evaluate_local_export_dry_run(
        export_plan=_plan(status="blocked"),
        artifact_source_path="output/candidates/candidate-0001/artifact.png",
    )

    assert dry_run["status"] == "blocked"
    assert dry_run["checks"]["plan_is_planned"] is False
