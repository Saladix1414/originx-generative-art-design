"""Prompt evidence chain for OX-MASTER-PROMPT-1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from oxgad.master_prompt.provenance import (
    build_prompt_provenance_hook,
)


PROMPT_EVIDENCE_CHAIN_VERSION = "OX-MASTER-PROMPT-EVIDENCE-CHAIN-1"


def build_prompt_evidence_chain(
    master_prompt: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a read-only prompt evidence chain."""

    hook = build_prompt_provenance_hook(
        master_prompt
    )

    return {
        "chainVersion": PROMPT_EVIDENCE_CHAIN_VERSION,
        "project": hook["project"],
        "promptId": hook["promptId"],
        "steps": [
            {
                "step": "art-spec",
                "hash": hook["artSpecHash"],
                "required": True,
            },
            {
                "step": "render-plan",
                "hash": hook["renderPlanHash"],
                "required": True,
            },
            {
                "step": "master-prompt",
                "hash": hook["masterPromptHash"],
                "required": True,
            },
            {
                "step": "prompt-provenance-hook",
                "hash": hook["masterPromptHash"],
                "required": True,
            },
        ],
        "runtimeTarget": hook["runtimeTarget"],
        "seed": hook["seed"],
        "compilerVersion": hook["compilerVersion"],
        "authority": hook["authority"],
        "complete": True,
    }


def verify_prompt_evidence_chain(
    chain: Mapping[str, Any],
) -> bool:
    """Verify structural completeness of a prompt evidence chain."""

    required_steps = [
        "art-spec",
        "render-plan",
        "master-prompt",
        "prompt-provenance-hook",
    ]

    steps = chain.get(
        "steps",
        [],
    )

    if len(steps) != len(required_steps):
        return False

    for expected, actual in zip(
        required_steps,
        steps,
    ):
        if actual.get("step") != expected:
            return False

        digest = actual.get("hash")

        if not (
            isinstance(digest, str)
            and len(digest) == 64
        ):
            return False

        if actual.get("required") is not True:
            return False

    return bool(
        chain.get("complete") is True
        and chain.get("authority", {}).get(
            "manualApprovalRequired"
        )
        is True
    )
