from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.master_prompt.catalog import load_master_prompt_catalog


MASTER_PROMPT_SCHEMA_PATH = Path("schemas/ox-master-prompt-1.schema.json")
PROMPT_COMPILER_VERSION = "OX-MASTER-PROMPT-COMPILER-1"


def _join(parts: list[str]) -> str:
    return ", ".join(part for part in parts if part)


def build_master_prompt_payload(
    *,
    prompt_id: str,
    identity_input_id: str,
    art_spec_hash: str,
    render_plan_hash: str,
    rarity_band: str,
    composition_profile: str,
    render_intent: str,
    runtime_target: str,
    model_requirement: str,
    seed: int,
    trait_families: list[str],
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = catalog or load_master_prompt_catalog()

    positive = _join(
        [
            catalog["positive_language"][0],
            catalog["positive_language"][1],
            f"composition profile {composition_profile}",
            f"rarity band {rarity_band}",
            f"render intent {render_intent}",
        ]
    )

    negative = _join(
        [
            *catalog["negative_language"],
            *catalog["safety_language"]["required_negative_terms"],
        ]
    )

    payload = {
        "schema_version": "ox-master-prompt-1",
        "project": "originx-generative-art-design",
        "prompt_id": prompt_id,
        "source": {
            "identity_input_id": identity_input_id,
            "art_spec_hash": art_spec_hash,
            "render_plan_hash": render_plan_hash,
        },
        "controlled_vocabulary": {
            "trait_families": trait_families,
            "rarity_band": rarity_band,
            "composition_profile": composition_profile,
            "render_intent": render_intent,
        },
        "render_binding": {
            "runtime_target": runtime_target,
            "model_requirement": model_requirement,
            "seed": seed,
        },
        "prompt": {
            "positive": positive,
            "negative": negative,
        },
        "detail_priorities": {
            "macro": list(catalog["detail_language"]["macro"]),
            "meso": list(catalog["detail_language"]["meso"]),
            "micro": list(catalog["detail_language"]["micro"]),
        },
        "safety_boundaries": {
            "local_first": True,
            "no_network": True,
            "no_external_provider_dependency": True,
            "no_uncontrolled_text": True,
            "no_franchise_style": True,
        },
        "provenance_hooks": {
            "catalog_schema_version": "ox-art-spec-expansion-1",
            "prompt_compiler_version": PROMPT_COMPILER_VERSION,
            "hash_required": True,
        },
    }

    schema = json.loads(
        MASTER_PROMPT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    jsonschema.validate(payload, schema)

    return payload
