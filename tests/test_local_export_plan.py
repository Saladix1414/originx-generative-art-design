import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.quality import build_local_export_plan


def _readiness(status="ready"):
    return {
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


def test_local_export_plan_matches_schema():
    plan = build_local_export_plan(
        export_id="export-0001",
        release_readiness=_readiness(),
        artifact_filename="artifact.png",
    )

    schema = json.loads(Path("schemas/ox-local-export-plan-1.schema.json").read_text())
    jsonschema.validate(plan, schema)

    assert plan["schema_version"] == "ox-local-export-plan-1"
    assert plan["status"] == "planned"
    assert plan["planned_paths"]["manifest_path"] == (
        "output/canonical/canonical-0001/manifest.json"
    )
    assert plan["planned_paths"]["artifact_path"] == (
        "output/canonical/canonical-0001/artifact.png"
    )


def test_local_export_plan_blocks_when_release_not_ready():
    plan = build_local_export_plan(
        export_id="export-0001",
        release_readiness=_readiness(status="blocked"),
        artifact_filename="artifact.png",
    )

    assert plan["status"] == "blocked"


def test_local_export_plan_rejects_unsafe_segments():
    with pytest.raises(ValueError, match="safe path segment"):
        build_local_export_plan(
            export_id="export-0001",
            release_readiness={
                **_readiness(),
                "canonical_id": "../escape",
            },
            artifact_filename="artifact.png",
        )

    with pytest.raises(ValueError, match="safe path segment"):
        build_local_export_plan(
            export_id="export-0001",
            release_readiness=_readiness(),
            artifact_filename="../artifact.png",
        )
