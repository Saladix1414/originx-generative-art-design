"""Genesis Art Spec and Render Plan preparation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.design.art_rules import art_rule_hash
from oxgad.design.integration import integrated_design_hash
from oxgad.genesis.identity import build_genesis_identity
from oxgad.genesis.lore import build_genesis_lore
from oxgad.render.compiler import compile_render_plan
from oxgad.structure.assembler import (
    ArtSpecAssembly,
    assemble_art_spec,
)
from oxgad.structure.canonical import (
    art_spec_hash,
    canonical_sha256,
)
from oxgad.structure.input import StructureInput
from oxgad.structure.validator import validate_art_spec


GENESIS_RENDER_BINDING_VERSION = (
    "OX-GENESIS-RENDER-BINDING-1"
)

GENESIS_RENDER_BINDING_SCHEMA_PATH = Path(
    "schemas/ox-genesis-render-binding-1.schema.json"
)

MODEL_HASH = (
    "sha256:"
    "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
    "fe0fa9af6c64c4829022261f"
)


def validate_genesis_render_binding(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        GENESIS_RENDER_BINDING_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)

    payload = dict(value)
    observed = payload.pop("bindingHash")

    if observed != canonical_sha256(payload):
        raise ValueError("Genesis render binding hash mismatch.")

    return value


def _structure_input(token_id: int) -> StructureInput:
    identity = build_genesis_identity(token_id)
    lore = build_genesis_lore(token_id)
    resonance = lore["resonance"]

    return StructureInput.from_mapping({
        "tokenId": identity["tokenId"],
        "serial": identity["serial"],
        "canonicalName": identity["canonicalName"],
        "tier": "LEGENDARY",
        "generationTheme": identity["generationTheme"],
        "dna": identity["dna"],
        "dnaHash": identity["dnaHash"],
        "seed": identity["seed"],
        "resonance": {
            "spectrum": resonance["spectrum"],
            "energyTopology": (
                resonance["resonanceClass"].lower()
                + "-glyph-topology"
            ),
            "intensity": round(
                resonance["pulse"] / 12,
                3,
            ),
            "narrativeRole": (
                "deterministic visual influence only"
            ),
        },
    })


def build_genesis_art_spec(
    token_id: int,
) -> ArtSpecAssembly:
    identity = build_genesis_identity(token_id)
    lore = build_genesis_lore(token_id)
    base = assemble_art_spec(_structure_input(token_id))
    value = copy.deepcopy(base.art_spec)

    dna = identity["dna"]
    resonance = lore["resonance"]
    glyph = lore["glyph"]

    value["dragon"]["body"]["form"] = dna["bodyStructure"]
    value["dragon"]["horns"]["form"] = (
        dna["hornArchitecture"]
    )
    value["dragon"]["wings"]["form"] = dna["wingGeometry"]
    value["dragon"]["mechanicalAugmentation"]["form"] = (
        dna["augmentation"]
    )
    value["pose"]["stance"] = dna["poseProfile"]

    value["environment"]["biome"] = dna["environment"]
    value["environment"]["architecture"]["form"] = (
        "gothic-megalithic-" + dna["environment"]
    )
    value["environment"]["weather"] = (
        "mineral fog, ash and controlled primordial storm"
    )
    value["environment"]["atmosphere"] = (
        "dark monumental primordial pressure"
    )

    value["materials"]["assignments"].update({
        "dragonPrimary": dna["primaryMaterial"],
        "dragonSecondary": dna["secondaryMaterial"],
        "environmentPrimary": "weathered-basalt",
        "energyAccent": resonance["spectrum"][0],
    })
    value["materials"]["libraryRefs"] = sorted(set(
        value["materials"]["libraryRefs"]
        + [
            "obsidian",
            "basalt",
            "weathered-stone",
            "dark-forged-metal",
        ]
    ))
    value["materials"]["weatheringPolicy"] = (
        "extreme physically coherent erosion, fractures, "
        "ash deposits and mineral variation"
    )

    value["lighting"]["key"] = dna["lightingProfile"]
    value["lighting"]["rim"] = resonance["spectrum"][0]
    value["lighting"]["contrast"] = 0.9
    value["lighting"]["exposureBias"] = -0.35

    value["colorPolicy"]["basePalette"] = [
        "obsidian-black",
        "basalt-grey",
        "weathered-stone",
    ]
    value["colorPolicy"]["accentPalette"] = [
        resonance["spectrum"][0],
        resonance["spectrum"][1],
    ]
    value["colorPolicy"]["energyPalette"] = [
        resonance["spectrum"][0],
    ]
    value["colorPolicy"]["neonLimit"] = 0.08
    value["colorPolicy"]["saturationPolicy"] = (
        "restrained mineral accents only"
    )

    value["resonance"].update({
        "spectrum": resonance["spectrum"],
        "strength": round(resonance["pulse"] / 12, 3),
        "energyTopology": (
            resonance["resonanceClass"].lower()
            + "-deterministic-topology"
        ),
        "glyphInfluence": (
            f"{glyph['geometry']['spokes']}-spoke rhythm; "
            f"{glyph['geometry']['rings']}-ring structural cadence"
        ),
        "accentGeometry": dna["hornArchitecture"],
        "lightingRhythm": dna["lightingProfile"],
        "atmosphericBehavior": (
            "mineral fog shaped by deterministic glyph geometry"
        ),
        "narrativeOnly": True,
    })

    value["renderIntent"].update({
        "targetResolution": {
            "width": 512,
            "height": 512,
        },
        "targetAspectRatio": "1:1",
        "styleIntent": (
            "monumental dark primordial dragon realism"
        ),
        "realism": 0.92,
        "cinematicWeight": 0.95,
        "detailDensity": 0.9,
        "preserveIdentity": True,
    })

    forbidden = set(
        value["negativeConstraints"]["forbiddenElements"]
    )
    forbidden.update({
        "generic fantasy dragon",
        "franchise-derived design",
        "cartoon",
        "excessive neon",
        "random text",
        "watermark",
        "uncontrolled cyberpunk",
        "duplicate limbs",
        "broken wings",
        "malformed anatomy",
    })
    value["negativeConstraints"]["forbiddenElements"] = sorted(
        forbidden
    )

    validate_art_spec(value)

    result = ArtSpecAssembly(
        art_spec=value,
        art_spec_hash=art_spec_hash(value),
        art_rule_hash=art_rule_hash(
            tier="LEGENDARY",
            seed=base.seed,
        ),
        design_hash=integrated_design_hash(
            tier="LEGENDARY",
            seed=base.seed,
        ),
        seed=base.seed,
    )

    compile_render_plan(result)
    return result


def build_genesis_render_binding(
    token_id: int,
) -> dict[str, Any]:
    identity = build_genesis_identity(token_id)
    assembly = build_genesis_art_spec(token_id)
    compilation = compile_render_plan(assembly)

    payload = {
        "bindingVersion": GENESIS_RENDER_BINDING_VERSION,
        "tokenId": token_id,
        "serial": identity["serial"],
        "artSpecHash": assembly.art_spec_hash,
        "renderPlanHash": compilation.render_plan_hash,
        "model": {
            "modelId": "OX-MODEL-002",
            "modelName": "Stable Diffusion 1.5",
            "productionAlias": "OX-GENESIS-MODEL-1",
            "modelHash": MODEL_HASH,
            "format": "GGUF",
            "quantization": "Q4_0",
        },
        "runtime": {
            "family": "stable-diffusion.cpp",
            "commit": (
                "792bcd344c3fa4d14143b240d5f6cbb324583b18"
            ),
            "target": "LOCAL_CPP",
            "paramsBackend": "disk",
            "mmap": True,
            "threads": 4,
            "vaeTiling": True,
            "vaeTileSize": "128x128",
        },
        "sampling": {
            "sampler": "euler_a",
            "scheduler": "discrete",
            "steps": 12,
            "cfg": 7.0,
            "seed": identity["seed"],
            "batchSize": 1,
        },
        "resolution": {
            "width": 512,
            "height": 512,
        },
        "detailPasses": [
            "MACRO_VALIDATION",
            "MESO_REVIEW",
            "MICRO_REVIEW",
        ],
        "upscalePlan": {
            "state": "DEFERRED_UNTIL_QUALITY_APPROVAL",
            "enabled": False,
        },
        "authority": {
            "candidateIsCanonical": False,
            "manualQualityReviewRequired": True,
            "minimumQualityScore": 92,
            "executionAllowed": False,
        },
    }

    value = {
        **payload,
        "bindingHash": canonical_sha256(payload),
    }
    validate_genesis_render_binding(value)
    return value


def build_genesis_batch_plans() -> tuple[
    dict[str, Any],
    ...,
]:
    values = []

    for token_id in range(1, 11):
        assembly = build_genesis_art_spec(token_id)
        compilation = compile_render_plan(assembly)
        binding = build_genesis_render_binding(token_id)

        values.append({
            "tokenId": token_id,
            "artSpec": assembly.art_spec,
            "artSpecHash": assembly.art_spec_hash,
            "renderPlan": compilation.render_plan,
            "renderPlanHash": compilation.render_plan_hash,
            "binding": binding,
        })

    for field in (
        "artSpecHash",
        "renderPlanHash",
    ):
        if len({item[field] for item in values}) != 10:
            raise RuntimeError(f"Duplicate {field}.")

    return tuple(values)
