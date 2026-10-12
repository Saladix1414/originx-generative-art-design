"""Deterministic identities for the Genesis Legendary cohort."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.structure.canonical import canonical_sha256


GENESIS_IDENTITY_VERSION = "OX-GENESIS-IDENTITY-1"
GENESIS_GENERATION_VERSION = "OX-GENESIS-GENERATION-1"
GENESIS_BATCH_ID = "GENESIS-BATCH-0001"
GENESIS_MAXIMUM_SUPPLY = 1000

GENESIS_IDENTITY_SCHEMA_PATH = Path(
    "schemas/ox-genesis-identity-1.schema.json"
)

_NAMES = (
    "Azhurak Primordialis",
    "Vaeltharos Monolith",
    "Korvaxion the First Ember",
    "Nytherion Basalt Crown",
    "Drakorym the Foundation",
    "Oryxath Megalith",
    "Zhaevor Ash Sovereign",
    "Tharokh Obsidian Wing",
    "Kaelzaryn Storm Reliquary",
    "Vyrnathos the Origin Seal",
)

_TITLES = (
    "The Primordial Witness",
    "Keeper of the First Monolith",
    "Bearer of the Foundation Flame",
    "Sovereign of the Basalt Crown",
    "Architect of the Ancient Deep",
    "Guardian of the Megalith Gate",
    "The Ash-Bound Origin",
    "Warden of the Obsidian Firmament",
    "Herald of the Founding Storm",
    "Bearer of the Origin Seal",
)

_BODY_FORMS = (
    "colossal-grounded",
    "monumental-serpentine",
    "massive-broad-chested",
    "fortress-backed",
    "ancient-predatory",
)

_HORN_ARCHITECTURES = (
    "forward-megalithic-crown",
    "radial-basal-arches",
    "asymmetric-cathedral-spires",
    "layered-obsidian-buttresses",
    "swept-architectural-blades",
)

_WING_GEOMETRIES = (
    "massive-ribbed-vault",
    "broad-basalt-fan",
    "cathedral-buttress-wing",
    "segmented-forged-membrane",
    "weathered-monumental-sail",
)

_POSES = (
    "grounded-apex-stance",
    "monumental-three-quarter-guard",
    "wings-raised-foundation-pose",
    "low-crouched-storm-defiance",
    "ascending-megalithic-profile",
)

_ENVIRONMENTS = (
    "basalt-origin-citadel",
    "obsidian-foundation-chasm",
    "cyclopean-storm-sanctum",
    "ash-covered-proto-forge",
    "mineral-fog-megalith-field",
)

_LIGHTING = (
    "restrained-cyan-rim",
    "deep-crimson-forge-rim",
    "cold-storm-toplight",
    "subsurface-mineral-glow",
    "eclipse-backlight",
)


def validate_genesis_identity(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        GENESIS_IDENTITY_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def _seed(identity_material: Mapping[str, Any]) -> int:
    digest = hashlib.sha256(
        json.dumps(
            identity_material,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).digest()

    return int.from_bytes(digest[:8], "big")


def build_genesis_identity(token_id: int) -> dict[str, Any]:
    if token_id < 1 or token_id > 10:
        raise ValueError(
            "Phase 79 supports only Genesis tokens #0001-#0010."
        )

    index = token_id - 1

    dna = {
        "dnaVersion": "OX-GENESIS-DNA-1",
        "archetype": "primordial-colossal-dragon",
        "bodyStructure": _BODY_FORMS[index % 5],
        "hornArchitecture": _HORN_ARCHITECTURES[index % 5],
        "wingGeometry": _WING_GEOMETRIES[(index * 2) % 5],
        "poseProfile": _POSES[(index * 3) % 5],
        "environment": _ENVIRONMENTS[(index * 4) % 5],
        "lightingProfile": _LIGHTING[(index * 2 + 1) % 5],
        "primaryMaterial": (
            "obsidian" if index % 2 == 0 else "basalt"
        ),
        "secondaryMaterial": (
            "dark-forged-metal"
            if index % 3
            else "weathered-stone"
        ),
        "augmentation": (
            "ancient-proto-technology"
        ),
        "lineage": {
            "cohort": "GENESIS",
            "era": "PRIMORDIAL ORIGIN",
            "tier": "LEGENDARY",
            "index": token_id,
            "maximumSupply": GENESIS_MAXIMUM_SUPPLY,
        },
    }

    dna_hash = canonical_sha256(dna)

    material = {
        "identityVersion": GENESIS_IDENTITY_VERSION,
        "tokenId": token_id,
        "serial": f"#{token_id:04d}",
        "canonicalName": _NAMES[index],
        "tier": "LEGENDARY",
        "cohort": "GENESIS",
        "era": "PRIMORDIAL ORIGIN",
        "dnaHash": dna_hash,
    }

    seed = _seed(material)

    value = {
        "identityVersion": GENESIS_IDENTITY_VERSION,
        "tokenId": token_id,
        "serial": f"#{token_id:04d}",
        "canonicalName": _NAMES[index],
        "title": _TITLES[index],
        "tier": "LEGENDARY",
        "cohort": "GENESIS",
        "era": "PRIMORDIAL ORIGIN",
        "structureProfileEra": "Ascended Origin",
        "generationVersion": GENESIS_GENERATION_VERSION,
        "generationTheme": "Genesis / Primordial Origin",
        "dna": dna,
        "dnaHash": dna_hash,
        "seed": seed,
        "seedHash": canonical_sha256({
            "seed": seed,
            "dnaHash": dna_hash,
            "tokenId": token_id,
        }),
        "modelBinding": {
            "modelId": "OX-MODEL-002",
            "productionAlias": "OX-GENESIS-MODEL-1",
            "modelHash": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "status": "CANDIDATE_PENDING_GENESIS_GATE",
        },
    }

    validate_genesis_identity(value)
    return value


def build_genesis_batch_identities() -> tuple[dict[str, Any], ...]:
    identities = tuple(
        build_genesis_identity(token_id)
        for token_id in range(1, 11)
    )

    names = {
        item["canonicalName"]
        for item in identities
    }
    dna_hashes = {
        item["dnaHash"]
        for item in identities
    }
    seeds = {
        item["seed"]
        for item in identities
    }

    if len(names) != 10:
        raise RuntimeError("Duplicate Genesis canonical name.")

    if len(dna_hashes) != 10:
        raise RuntimeError("Duplicate Genesis DNA.")

    if len(seeds) != 10:
        raise RuntimeError("Duplicate Genesis seed.")

    return identities
