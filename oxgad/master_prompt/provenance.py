"""Prompt provenance hook for OX-MASTER-PROMPT-1 payloads."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from oxgad.master_prompt.canonical import master_prompt_hash


PROMPT_PROVENANCE_HOOK_VERSION = "OX-MASTER-PROMPT-PROVENANCE-HOOK-1"


def stable_prompt_hash(
    master_prompt: Mapping[str, Any],
) -> str:
    """Hash a prompt while excluding self-referential hash fields."""

    payload = deepcopy(
        dict(master_prompt)
    )

    render_binding = payload.get(
        "render_binding"
    )

    if isinstance(render_binding, dict):
        render_binding.pop(
            "master_prompt_hash",
            None,
        )

    return master_prompt_hash(
        payload
    )


def _hook_flag(
    provenance_hooks: Mapping[str, Any],
    snake_name: str,
    camel_name: str,
) -> bool:
    if snake_name in provenance_hooks:
        return bool(
            provenance_hooks[snake_name]
        )

    if camel_name in provenance_hooks:
        return bool(
            provenance_hooks[camel_name]
        )

    return False


def _compiler_version(
    master_prompt: Mapping[str, Any],
    render_binding: Mapping[str, Any],
) -> str:
    compiler = master_prompt.get(
        "compiler",
        {},
    )

    if not isinstance(compiler, Mapping):
        compiler = {}

    return str(
        render_binding.get(
            "compiler_version",
            compiler.get(
                "version",
                PROMPT_PROVENANCE_HOOK_VERSION,
            ),
        )
    )


def build_prompt_provenance_hook(
    master_prompt: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a provenance-ready evidence record for a master prompt."""

    source = master_prompt["source"]
    render_binding = master_prompt["render_binding"]
    provenance_hooks = master_prompt["provenance_hooks"]

    prompt_hash = stable_prompt_hash(
        master_prompt
    )

    expected_prompt_hash = render_binding.get(
        "master_prompt_hash"
    )

    if (
        expected_prompt_hash is not None
        and expected_prompt_hash != prompt_hash
    ):
        raise ValueError("Master prompt hash mismatch.")

    return {
        "hookVersion": PROMPT_PROVENANCE_HOOK_VERSION,
        "schemaVersion": master_prompt["schema_version"],
        "project": master_prompt["project"],
        "promptId": master_prompt["prompt_id"],
        "masterPromptHash": prompt_hash,
        "identityInputId": source["identity_input_id"],
        "artSpecHash": source["art_spec_hash"],
        "renderPlanHash": source["render_plan_hash"],
        "runtimeTarget": render_binding["runtime_target"],
        "seed": render_binding["seed"],
        "compilerVersion": _compiler_version(
            master_prompt,
            render_binding,
        ),
        "provenanceHooks": {
            "recordsArtSpecHash": _hook_flag(
                provenance_hooks,
                "records_art_spec_hash",
                "recordsArtSpecHash",
            ),
            "recordsRenderPlanHash": _hook_flag(
                provenance_hooks,
                "records_render_plan_hash",
                "recordsRenderPlanHash",
            ),
            "recordsModelHash": _hook_flag(
                provenance_hooks,
                "records_model_hash",
                "recordsModelHash",
            ),
            "recordsMediaHash": _hook_flag(
                provenance_hooks,
                "records_media_hash",
                "recordsMediaHash",
            ),
            "recordsSeed": _hook_flag(
                provenance_hooks,
                "records_seed",
                "recordsSeed",
            ),
        },
        "authority": {
            "candidateIsCanonical": False,
            "aiOutputIsCanonical": False,
            "manualApprovalRequired": True,
        },
    }
