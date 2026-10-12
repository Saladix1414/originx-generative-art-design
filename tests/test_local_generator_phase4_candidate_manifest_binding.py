import json
from pathlib import Path

import jsonschema

from oxgad.forge import (
    build_candidate_manifest,
    build_execution_decision,
    build_unapproved_candidate_output,
    candidate_manifest_hash,
    validate_candidate_manifest,
)


SCHEMA = Path("schemas/ox-candidate-manifest-1.schema.json")


def _forge_contract():
    return {
        "forgeVersion": "OX-LOCAL-FORGE-1",
        "source": {
            "renderPlanVersion": "OX-RENDER-1",
            "renderPlanHash": "sha256:" + "a" * 64,
        },
        "hardware": {
            "profileVersion": "OX-HARDWARE-PROFILE-1",
            "requestedTarget": "LOCAL_CPP",
            "capability": "UNKNOWN",
        },
        "model": {
            "bindingState": "UNBOUND",
        },
        "execution": {
            "policy": "LOCAL_FIRST",
            "mode": "PREPARE_ONLY",
            "authorizationState": "BLOCKED",
            "executionAllowed": False,
        },
        "output": {
            "mediaGenerationAllowed": False,
            "canonicalArtworkAllowed": False,
        },
    }


def _decision():
    return build_execution_decision(
        _forge_contract()
    )


def _candidate():
    return build_unapproved_candidate_output(
        candidate_id="candidate-token-0001-local-001",
        media_path="output/candidates/token-0001/candidate-001.png",
        render_plan_hash="sha256:" + "a" * 64,
        execution_decision_hash="sha256:" + "b" * 64,
        model_binding_hash=None,
    )


def _manifest():
    return build_candidate_manifest(
        candidate_output=_candidate(),
        execution_decision=_decision(),
    )


def test_candidate_manifest_schema_is_valid_draft_2020_12():
    schema = json.loads(
        SCHEMA.read_text()
    )

    jsonschema.Draft202012Validator.check_schema(
        schema
    )


def test_candidate_manifest_links_candidate_and_decision():
    manifest = _manifest()

    assert manifest["manifestVersion"] == "OX-CANDIDATE-MANIFEST-1"
    assert manifest["candidateId"] == "candidate-token-0001-local-001"
    assert manifest["state"] == "CANDIDATE_MANIFEST_PREPARED"
    assert manifest["links"]["candidateOutputHash"].startswith("sha256:")
    assert manifest["links"]["executionDecisionHash"].startswith("sha256:")


def test_candidate_manifest_preserves_non_authority():
    manifest = _manifest()

    assert manifest["authority"] == {
        "mediaGenerated": False,
        "candidateIsCanonical": False,
        "manualApprovalRequired": True,
        "backendInvocationAllowed": False,
    }


def test_candidate_manifest_validates_against_schema():
    manifest = _manifest()

    assert validate_candidate_manifest(
        manifest
    ) == manifest


def test_candidate_manifest_hash_is_stable():
    first = _manifest()
    second = _manifest()

    assert candidate_manifest_hash(first) == candidate_manifest_hash(second)
