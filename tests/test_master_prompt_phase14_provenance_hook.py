import json
from pathlib import Path

import pytest

from oxgad.master_prompt import (
    PROMPT_PROVENANCE_HOOK_VERSION,
    build_prompt_provenance_hook,
    stable_prompt_hash,
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


def test_prompt_provenance_hook_contains_required_evidence():
    prompt = _prompt()

    hook = build_prompt_provenance_hook(
        prompt
    )

    assert hook["hookVersion"] == PROMPT_PROVENANCE_HOOK_VERSION
    assert hook["schemaVersion"] == "ox-master-prompt-1"
    assert hook["project"] == "originx-generative-art-design"
    assert hook["promptId"] == prompt["prompt_id"]
    assert hook["masterPromptHash"] == stable_prompt_hash(
        prompt
    )
    assert hook["artSpecHash"] == prompt["source"]["art_spec_hash"]
    assert hook["renderPlanHash"] == prompt["source"]["render_plan_hash"]
    assert hook["runtimeTarget"] == prompt["render_binding"]["runtime_target"]
    assert hook["seed"] == prompt["render_binding"]["seed"]


def test_prompt_provenance_hook_keeps_non_authority_boundaries():
    hook = build_prompt_provenance_hook(
        _prompt()
    )

    assert hook["authority"] == {
        "candidateIsCanonical": False,
        "aiOutputIsCanonical": False,
        "manualApprovalRequired": True,
    }


def test_prompt_provenance_hook_rejects_hash_mismatch():
    prompt = _prompt()
    prompt["render_binding"]["master_prompt_hash"] = "0" * 64

    with pytest.raises(
        ValueError,
        match="Master prompt hash mismatch",
    ):
        build_prompt_provenance_hook(
            prompt
        )
