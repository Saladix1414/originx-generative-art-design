"""Bind OX-RENDER-1 plans to OX-MASTER-PROMPT-1 payloads."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from oxgad.master_prompt.binding import build_master_prompt_from_art_spec
from oxgad.master_prompt.canonical import master_prompt_hash
from oxgad.structure.canonical import canonical_sha256


def _hex_digest(value: str) -> str:
    if value.startswith("sha256:"):
        value = value.split(":", 1)[1]

    if len(value) != 64:
        raise ValueError("Expected a 64-character SHA-256 digest.")

    int(value, 16)
    return value


def render_plan_hash(render_plan: Mapping[str, Any]) -> str:
    """Return the canonical OX-RENDER-1 hash as plain hex."""

    return _hex_digest(
        canonical_sha256(render_plan)
    )


def build_render_bound_master_prompt(
    *,
    prompt_id: str,
    identity_input_id: str,
    art_spec: Mapping[str, Any],
    render_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a prompt payload bound to the render compiler output."""

    payload = build_master_prompt_from_art_spec(
        prompt_id=prompt_id,
        identity_input_id=identity_input_id,
        art_spec=art_spec,
        render_plan=render_plan,
    )

    source = payload["source"]
    expected_hash = render_plan_hash(render_plan)

    if source["render_plan_hash"] != expected_hash:
        raise ValueError("Render plan hash mismatch.")

    payload["render_binding"]["render_plan_hash"] = expected_hash
    payload["render_binding"]["master_prompt_hash"] = master_prompt_hash(
        payload
    )

    if (
        payload["render_binding"]["seed"]
        != render_plan["seed"]
    ):
        raise ValueError("Render seed mismatch.")

    if (
        payload["render_binding"]["runtime_target"]
        != render_plan["runtimeTarget"]
    ):
        raise ValueError("Render runtime target mismatch.")

    return payload
