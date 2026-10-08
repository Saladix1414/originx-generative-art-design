import json
from pathlib import Path

from oxgad.master_prompt import (
    PROMPT_EVIDENCE_CHAIN_VERSION,
    build_prompt_evidence_chain,
    stable_prompt_hash,
    verify_prompt_evidence_chain,
)


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")


def _prompt():
    payload = json.loads(
        FIXTURE.read_text()
    )

    payload["render_binding"]["master_prompt_hash"] = stable_prompt_hash(
        payload
    )

    return payload


def test_prompt_evidence_chain_contains_canonical_steps():
    chain = build_prompt_evidence_chain(
        _prompt()
    )

    assert chain["chainVersion"] == PROMPT_EVIDENCE_CHAIN_VERSION
    assert [
        step["step"]
        for step in chain["steps"]
    ] == [
        "art-spec",
        "render-plan",
        "master-prompt",
        "prompt-provenance-hook",
    ]
    assert chain["complete"] is True
    assert chain["authority"]["manualApprovalRequired"] is True


def test_prompt_evidence_chain_verifies_valid_chain():
    chain = build_prompt_evidence_chain(
        _prompt()
    )

    assert verify_prompt_evidence_chain(
        chain
    ) is True


def test_prompt_evidence_chain_rejects_missing_step():
    chain = build_prompt_evidence_chain(
        _prompt()
    )
    chain["steps"] = chain["steps"][:-1]

    assert verify_prompt_evidence_chain(
        chain
    ) is False


def test_prompt_evidence_chain_rejects_bad_hash():
    chain = build_prompt_evidence_chain(
        _prompt()
    )
    chain["steps"][0]["hash"] = "not-a-hash"

    assert verify_prompt_evidence_chain(
        chain
    ) is False
