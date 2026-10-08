from __future__ import annotations

from typing import Any

from oxgad.master_prompt.builder import build_master_prompt_payload
from oxgad.structure.canonical import art_spec_hash, canonical_sha256



def _hex_digest(value: str) -> str:
    if value.startswith("sha256:"):
        return value.split(":", 1)[1]

    return value


def _tier_to_rarity(tier: str) -> str:
    normalized = tier.strip().lower()

    if normalized in {"common", "uncommon", "rare", "epic", "legendary"}:
        return normalized

    return "rare"


def _composition_profile(art_spec: dict[str, Any]) -> str:
    composition = art_spec.get("composition", {})
    framing = art_spec.get("framing", {})

    combined = f"{composition} {framing}".lower()

    if "radial" in combined:
        return "radial_field"

    if "landscape" in combined:
        return "layered_landscape"

    if "orbital" in combined:
        return "orbital_system"

    return "centered_icon"


def _render_intent(art_spec: dict[str, Any]) -> str:
    render_intent = art_spec.get("renderIntent", {})
    value = str(
        render_intent.get("intent")
        or render_intent.get("profile")
        or render_intent.get("name")
        or "candidate"
    ).strip().lower()

    if value in {"preview", "candidate", "canonical", "high_detail"}:
        return value

    return "candidate"


def build_master_prompt_from_art_spec(
    *,
    prompt_id: str,
    identity_input_id: str,
    art_spec: dict[str, Any],
    render_plan: dict[str, Any],
) -> dict[str, Any]:
    identity = art_spec.get("identity", {})
    tier = str(identity.get("tier", "rare"))

    render_plan_hash = _hex_digest(canonical_sha256(render_plan))

    return build_master_prompt_payload(
        prompt_id=prompt_id,
        identity_input_id=identity_input_id,
        art_spec_hash=_hex_digest(art_spec_hash(art_spec)),
        render_plan_hash=render_plan_hash,
        rarity_band=_tier_to_rarity(tier),
        composition_profile=_composition_profile(art_spec),
        render_intent=_render_intent(art_spec),
        runtime_target=str(render_plan.get("runtimeTarget", "LOCAL_CPP")),
        model_requirement=str(render_plan.get("modelRequirement", "local diffusion model")),
        seed=int(render_plan.get("seed", art_spec.get("seed", 0))),
        trait_families=[
            "palette",
            "geometry",
            "material",
            "lighting",
        ],
    )
