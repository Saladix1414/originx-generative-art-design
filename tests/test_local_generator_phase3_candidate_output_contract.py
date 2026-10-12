import json
from pathlib import Path

import jsonschema

from oxgad.forge import (
    build_unapproved_candidate_output,
    candidate_output_hash,
    validate_candidate_output,
)


SCHEMA = Path("schemas/ox-candidate-output-1.schema.json")


def _candidate():
    return build_unapproved_candidate_output(
        candidate_id="candidate-token-0001-local-001",
        media_path="output/candidates/token-0001/candidate-001.png",
        render_plan_hash="sha256:" + "a" * 64,
        execution_decision_hash="sha256:" + "b" * 64,
        model_binding_hash=None,
    )


def test_candidate_output_schema_is_valid_draft_2020_12():
    schema = json.loads(
        SCHEMA.read_text()
    )

    jsonschema.Draft202012Validator.check_schema(
        schema
    )


def test_candidate_output_is_unapproved_by_default():
    candidate = _candidate()

    assert candidate["candidateVersion"] == "OX-CANDIDATE-OUTPUT-1"
    assert candidate["state"] == "CANDIDATE_UNAPPROVED"
    assert candidate["media"]["mediaHash"] is None
    assert candidate["quality"]["qualityGateStatus"] == "NOT_REVIEWED"
    assert candidate["quality"]["canonicalPromotionAllowed"] is False
    assert candidate["authority"] == {
        "candidateIsCanonical": False,
        "manualApprovalRequired": True,
        "aiOutputIsCanonical": False,
    }


def test_candidate_output_validates_against_schema():
    candidate = _candidate()

    assert validate_candidate_output(
        candidate
    ) == candidate


def test_candidate_output_rejects_unsafe_path():
    candidate = _candidate()
    candidate["media"]["path"] = "../outside.png"

    try:
        validate_candidate_output(
            candidate
        )
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Candidate accepted unsafe media path."
        )


def test_candidate_output_hash_is_stable():
    first = _candidate()
    second = _candidate()

    assert candidate_output_hash(first) == candidate_output_hash(second)
