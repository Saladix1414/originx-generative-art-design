import json
from pathlib import Path

import jsonschema

from oxgad.forge import (
    build_candidate_manifest,
    build_candidate_provenance_hook,
    build_execution_decision,
    build_unapproved_candidate_output,
    candidate_provenance_hook_hash,
    validate_candidate_provenance_hook,
)


SCHEMA = Path("schemas/ox-candidate-provenance-hook-1.schema.json")


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


def _hook():
    return build_candidate_provenance_hook(
        candidate_output=_candidate(),
        candidate_manifest=_manifest(),
        execution_decision=_decision(),
    )


def test_candidate_provenance_schema_is_valid_draft_2020_12():
    schema = json.loads(
        SCHEMA.read_text()
    )

    jsonschema.Draft202012Validator.check_schema(
        schema
    )


def test_candidate_provenance_hook_links_prepared_candidate():
    hook = _hook()

    assert hook["hookVersion"] == "OX-CANDIDATE-PROVENANCE-HOOK-1"
    assert hook["candidateId"] == "candidate-token-0001-local-001"
    assert hook["state"] == "PROVENANCE_PREPARED"
    assert hook["links"]["candidateOutputHash"].startswith("sha256:")
    assert hook["links"]["candidateManifestHash"].startswith("sha256:")
    assert hook["links"]["executionDecisionHash"].startswith("sha256:")


def test_candidate_provenance_hook_preserves_no_media_generated():
    hook = _hook()

    assert hook["media"] == {
        "mediaGenerated": False,
        "mediaHash": None,
        "path": "output/candidates/token-0001/candidate-001.png",
    }
    assert hook["authority"] == {
        "candidateIsCanonical": False,
        "manualApprovalRequired": True,
        "backendInvocationAllowed": False,
        "aiOutputIsCanonical": False,
    }


def test_candidate_provenance_hook_validates_against_schema():
    hook = _hook()

    assert validate_candidate_provenance_hook(
        hook
    ) == hook


def test_candidate_provenance_hook_hash_is_stable():
    first = _hook()
    second = _hook()

    assert candidate_provenance_hook_hash(first) == candidate_provenance_hook_hash(second)
