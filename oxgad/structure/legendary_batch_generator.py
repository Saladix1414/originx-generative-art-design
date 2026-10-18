from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from oxgad.render.dragon_prompt_compiler import (
    compile_negative_prompt,
    compile_positive_prompt,
)
from oxgad.structure.dragon_identity_rules import (
    validate_coherence,
    validate_individuality,
)


GENERATION_VERSION = "OX-GENESIS-1"
BATCH_ID = "GENESIS-BATCH-0001"

SPEC_DIR = (
    ROOT
    / "output"
    / "specs"
    / "genesis-batch-0001"
)

PROMPT_DIR = (
    ROOT
    / "output"
    / "prompts"
    / "genesis-batch-0001"
)

MANIFEST_PATH = (
    ROOT
    / "output"
    / "manifests"
    / "genesis-batch-0001.json"
)


NAMES = [
    ("Vaerkaion", "The Obsidian Oath"),
    ("Morvathen", "The Tempest Crown"),
    ("Zerakthul", "The Ashen Covenant"),
    ("Aethrakar", "The Silent Monolith"),
    ("Korvaxis", "The Crimson Tribunal"),
    ("Nhalgorim", "The Keeper Below"),
    ("Tharvexis", "The Rune Devourer"),
    ("Vorlathen", "The Hollow Sovereign"),
    ("Iraekor", "The Shattered Sun"),
    ("Draevorn", "The Last Bastion"),
]

ARCHETYPES = [
    "RELIC_BEARER",
    "STORM_TYRANT",
    "ASHEN_PROPHET",
    "TEMPLE_GUARDIAN",
    "EXECUTIONER",
    "ABYSSAL_MONARCH",
    "RUNE_SOVEREIGN",
    "VOID_HUNTER",
    "WARLORD",
    "SENTINEL",
]

TEMPERAMENTS = [
    "COLD_SOVEREIGN",
    "CALCULATING",
    "ASCETIC_ANCIENT",
    "VIGILANT_PATIENT",
    "WRATHFUL_CONTAINED",
    "NOBLE_SEVERE",
    "RITUALISTIC",
    "SAVAGE_DISCIPLINED",
    "MOURNFUL_CURSED",
    "VIGILANT_PATIENT",
]

COMBAT_ROLES = [
    "RELIC_DEFENDER",
    "AERIAL_HUNTER",
    "HEX_CHANNELER",
    "WARDEN",
    "EXECUTIONER_MONARCH",
    "SIEGE_BREAKER",
    "TEMPEST_CASTER",
    "DUELIST_PREDATOR",
    "FRONTLINE_DESTROYER",
    "WARDEN",
]

WEAPONS = [
    "CHAINED_GREATSWORD",
    "NONE",
    "RITUAL_STAFF",
    "NONE",
    "OBSIDIAN_HALBERD",
    "RELIC_CHAIN",
    "NONE",
    "ENERGY_FORGED_CLAWS",
    "CEREMONIAL_SPEAR",
    "NONE",
]

ABILITIES = [
    "ABYSSAL_FLAME",
    "THUNDER_RESONANCE",
    "ASH_MANIPULATION",
    "GRAVITIC_PRESSURE",
    "CRIMSON_CURSE",
    "SEISMIC_FORCE",
    "RUNE_IGNITION",
    "VOID_BREATH",
    "OBSIDIAN_SHARD_PROJECTION",
    "FOG_CONCEALMENT",
]

BODY_STRUCTURES = [
    "HEAVY_QUADRUPED_MONUMENTAL",
    "ATHLETIC_AERIAL_PREDATOR",
    "LEAN_ANCIENT_SERPENTINE",
    "FORTRESS_HEAVY_GUARDIAN",
    "MASSIVE_EXECUTIONER_FRAME",
    "COLOSSAL_DEEP_CHESTED",
    "TALL_RITUAL_SOVEREIGN",
    "LOW_PREDATORY_STALKER",
    "BROAD_WARLORD_FRAME",
    "ARMORED_SENTINEL_FRAME",
]

HORN_STYLES = [
    "ARCHITECTURAL_BACKWARD_ASYMMETRIC",
    "FORKED_LIGHTNING_ARCH",
    "ASHEN_CROWN_BRANCHES",
    "MEGALITHIC_VERTICAL_SPIRES",
    "FORWARD_EXECUTIONER_HOOKS",
    "ABYSSAL_CROWN_RING",
    "RUNIC_HELIX_HORNS",
    "VOID_SWEPT_BLADES",
    "WAR_CREST_RAM_HORNS",
    "SENTINEL_STONE_CROWN",
]

WING_STYLES = [
    "BLADED_MEMBRANE_COLOSSAL",
    "LONG_RAZORED_STORM_WINGS",
    "TORN_ASHEN_CATHEDRAL_WINGS",
    "STONE_RIBBED_GUARDIAN_WINGS",
    "HEAVY_EXECUTIONER_WINGS",
    "ABYSSAL_VEILED_WINGS",
    "RUNIC_GEOMETRIC_WINGS",
    "NARROW_VOID_HUNTER_WINGS",
    "BATTLE_SCARRED_WAR_WINGS",
    "FORTRESS_SHIELD_WINGS",
]

SILHOUETTES = [
    "SOVEREIGN_SPIKED_MASSIVE",
    "AERIAL_FORKED_PREDATOR",
    "ASCETIC_SERPENTINE_PROPHET",
    "FORTRESS_MONOLITH_GUARDIAN",
    "EXECUTIONER_BLADED_HEAVY",
    "CROWNED_ABYSSAL_COLOSSUS",
    "RUNIC_TALL_SOVEREIGN",
    "LOW_VOID_STALKER",
    "BROAD_WARLORD_TITAN",
    "ARMORED_SENTINEL_MONOLITH",
]

SETTINGS = [
    "COLOSSAL_RUINED_GOTHIC_CITADEL_PLATFORM",
    "MEGALITHIC_SPIRE_SUMMIT",
    "ASHEN_CATHEDRAL_CRATER",
    "ANCIENT_GATE_FORTRESS",
    "BLACK_TRIBUNAL_COURTYARD",
    "ABYSSAL_THRONE_CHASM",
    "RUNIC_OBSERVATORY",
    "VOID_HUNTING_PASSAGE",
    "WAR_TORN_MEgalITHIC_PLAZA",
    "FORGOTTEN_SENTINEL_GATE",
]

GEOMETRIES = [
    "RADIAL_FRACTURED_NINEFOLD",
    "FORKED_STORM_HEXAGON",
    "ASH_SPIRAL_SEVENFOLD",
    "MONOLITHIC_CROSS_AXIS",
    "CRIMSON_TRIAD_BLADE",
    "ABYSSAL_CONCENTRIC_RING",
    "RUNIC_TWELVEFOLD_LATTICE",
    "VOID_BROKEN_CRESCENT",
    "WAR_SIGIL_OCTAGON",
    "SENTINEL_SQUARE_CROWN",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def deterministic_seed(
    token_id: int,
) -> int:
    digest = sha256_text(
        f"ORIGINX|{GENERATION_VERSION}|{token_id}"
    )

    return int(
        digest[:8],
        16,
    )


def resonance_payload(
    token_id: int,
    dna_seed_hash: str,
) -> dict[str, Any]:
    source = sha256_text(
        "ORIGINX_RESONANCE"
        f"|{GENERATION_VERSION}"
        f"|{token_id}"
        f"|{dna_seed_hash}"
    )

    primary = (
        int(source[0:4], 16)
        % 900
    ) + 100

    secondary = (
        int(source[4:8], 16)
        % 900
    ) + 100

    phase = (
        int(source[8:12], 16)
        % 360
    )

    pulse_modes = [
        "GRAVITIC_SLOW",
        "TEMPEST_RAPID",
        "RITUAL_STEADY",
        "ABYSSAL_DEEP",
        "FRACTURED_PULSE",
    ]

    pulse = pulse_modes[
        int(source[12:14], 16)
        % len(pulse_modes)
    ]

    return {
        "resonanceVersion": "OX-RESONANCE-1",
        "resonanceId": (
            f"ORX-RES-{token_id:04d}"
        ),
        "resonanceClass": (
            ARCHETYPES[token_id - 1]
            + "_RESONANCE"
        ),
        "resonanceSignature": source,
        "spectrum": (
            "OBSIDIAN_CYAN_CRIMSON"
        ),
        "primaryFrequency": primary,
        "secondaryFrequency": secondary,
        "pulse": pulse,
        "phaseDegrees": phase,
        "glyphSeed": sha256_text(
            f"ORIGINX_GLYPH|{source}"
        ),
        "semanticNote": (
            "Artistic and mathematical identity. "
            "Not a scientific or spiritual measurement."
        ),
    }


def build_spec(
    token_id: int,
) -> dict[str, Any]:
    index = token_id - 1

    if not 0 <= index < 10:
        raise ValueError(
            "This phase only permits tokenIds 1..10"
        )

    name, title = NAMES[index]

    seed = deterministic_seed(
        token_id
    )

    dna_seed_hash = sha256_text(
        "ORIGINX_DNA_SEED"
        f"|{GENERATION_VERSION}"
        f"|{token_id}"
        f"|{seed}"
    )

    resonance = resonance_payload(
        token_id,
        dna_seed_hash,
    )

    weapon = WEAPONS[index]

    has_weapon = (
        weapon != "NONE"
    )

    has_relic = index in {
        0,
        2,
        5,
        6,
    }

    power_expression = [
        f"{ABILITIES[index]}_BODY_MANIFESTATION",
        "RESONANCE_GLYPH_IGNITION",
        "ENVIRONMENTAL_RESPONSE",
    ]

    spec: dict[str, Any] = {
        "identity": {
            "tokenId": token_id,
            "serial": (
                f"#{token_id:04d}"
            ),
            "canonicalName": name,
            "title": title,
            "epithet": title,
            "tier": "LEGENDARY",
            "cohort": "GENESIS",
            "era": "PRIMORDIAL_ORIGIN",
            "generationVersion": (
                GENERATION_VERSION
            ),
            "seed": seed,
        },

        "dna": {
            "bindingStatus": (
                "PENDING_CANONICAL_DNA_ENGINE_BINDING"
            ),
            "dnaSeedHash": dna_seed_hash,
            "note": (
                "This phase does not replace the "
                "canonical OriginX DNA engine."
            ),
        },

        "classification": {
            "archetype": ARCHETYPES[index],
            "temperament": (
                TEMPERAMENTS[index]
            ),
            "presence": (
                "ANCIENT_MONUMENTAL_SOVEREIGN"
            ),
            "combatRole": (
                COMBAT_ROLES[index]
            ),
            "domain": SETTINGS[index],
            "moralTone": (
                "DARK_MYTHIC_NEUTRAL"
            ),
        },

        "anatomy": {
            "bodyStructure": (
                BODY_STRUCTURES[index]
            ),
            "headStyle": (
                "ORIGINAL_REGAL_PREDATORY"
            ),
            "hornStyle": (
                HORN_STYLES[index]
            ),
            "jawType": (
                "ARMORED_SCARRED"
            ),
            "eyeType": (
                "DEEP_SET_RESONANT"
            ),
            "wingStyle": (
                WING_STYLES[index]
            ),
            "tailStyle": (
                "HEAVY_COMBAT_TAIL"
            ),
            "limbStyle": (
                "POWERFUL_CLAWED"
            ),
            "silhouetteProfile": (
                SILHOUETTES[index]
            ),
        },

        "materials": {
            "primaryMaterial": (
                "OBSIDIAN_SCALE"
            ),
            "secondaryMaterial": (
                "BASALT_PLATING"
            ),
            "tertiaryMaterial": (
                "DARK_FORGED_STEEL"
            ),
            "boneLanguage": (
                "CARVED_ANCIENT_RIDGES"
            ),
            "surfaceAge": (
                "WEATHERED_ANCIENT"
            ),
            "damageProfile": (
                "SCARRED_FRACTURED_ERODED"
            ),
            "microSurface": [
                "MINERAL_DEPOSITS",
                "SCRATCHED_SURFACE",
                "ASH_DUST",
                "RUNE_ENGRAVINGS",
            ],
        },

        "armorAndRelics": {
            "hasArmor": True,
            "armorProfile": (
                "ORIGINX_RITUAL_BATTLE_ARMOR"
            ),
            "hasWeapon": has_weapon,
            "weaponType": weapon,
            "weaponMaterial": (
                "OBSIDIAN_DARK_STEEL"
                if has_weapon
                else "NONE"
            ),
            "weaponUseStyle": (
                COMBAT_ROLES[index]
                if has_weapon
                else "NATURAL_POWER_DOMINANT"
            ),
            "hasEmbeddedRelic": has_relic,
            "relicType": (
                "ANCIENT_RESONANCE_RELIC"
                if has_relic
                else "NONE"
            ),
        },

        "powers": {
            "signatureAbility": (
                ABILITIES[index]
            ),
            "energyMode": (
                "CONTROLLED_RESONANCE_MANIFESTATION"
            ),
            "powerExpression": (
                power_expression
            ),
            "breathType": (
                ABILITIES[index]
            ),
            "environmentInteraction": (
                "POWER_ALTERS_LOCAL_ATMOSPHERE"
            ),
        },

        "resonance": resonance,

        "glyph": {
            "glyphVersion": (
                "OX-GLYPH-1"
            ),
            "geometry": (
                GEOMETRIES[index]
            ),
            "influenceAreas": [
                "HORN_RHYTHM",
                "CHEST_FISSURES",
                "WING_GEOMETRY",
                "ENVIRONMENT_SIGILS",
                "LIGHT_PATTERN",
            ],
        },

        "environment": {
            "setting": SETTINGS[index],
            "architecture": (
                "ANCIENT_GOTHIC_MEGALITHIC"
            ),
            "weather": (
                "ASH_RAIN_FOG"
            ),
            "atmosphere": (
                "DARK_CINEMATIC_MINERAL_HAZE"
            ),
            "scale": "TITANIC",
            "foregroundElements": [
                "BROKEN_MONOLITHS",
                "ANCIENT_SIGIL_STONE",
                "MINERAL_DUST",
            ],
        },

        "composition": {
            "cameraAngle": (
                "LOW_THREE_QUARTER_CINEMATIC"
            ),
            "framing": (
                "FULL_BODY_DOMINANT"
            ),
            "pose": (
                "INDIVIDUAL_SOVEREIGN_POSE"
            ),
            "silhouettePriority": (
                "HIGH"
            ),
            "focalPriority": [
                "HEAD",
                "TORSO",
                "POWER_OR_WEAPON",
                "WINGS",
            ],
            "negativeSpaceControl": (
                "BALANCED"
            ),
            "storyBeat": (
                f"{ARCHETYPES[index]}"
                "_REVEALED"
            ),
        },

        "lighting": {
            "keyLight": (
                "MOONLIT_COLD"
            ),
            "rimLight": (
                "CONTROLLED_RESONANCE"
            ),
            "accentLight": (
                "SUBTLE_CYAN_CRIMSON"
            ),
            "contrastLevel": (
                "HIGH_CINEMATIC"
            ),
            "shadowStyle": (
                "DEEP_HEAVY"
            ),
        },

        "detailPolicy": {
            "macroPriority": [
                "ANATOMY",
                "SILHOUETTE",
                "POSE",
                "COMPOSITION",
            ],
            "mesoPriority": [
                "WINGS",
                "HORNS",
                "ARMOR",
                "MATERIAL_REGIONS",
            ],
            "microPriority": [
                "SCALE_TEXTURE",
                "SCRATCHES",
                "FRACTURES",
                "RUNE_ENGRAVINGS",
                "EYE_TEXTURE",
                "MINERAL_DUST",
            ],
        },

        "qualityTarget": {
            "minimumScore": 92,
            "mustPass": [
                "anatomyScore",
                "silhouetteScore",
                "compositionScore",
                "materialScore",
                "identityConsistencyScore",
                "visualGrammarScore",
            ],
        },

        "akashic": {
            "recordVersion": (
                "OX-AKASHIC-1"
            ),
            "initialEvents": [
                "DNA_FORGED",
                "NAME_ASSIGNED",
                "RESONANCE_CREATED",
                "RESONANCE_GLYPH_MANIFESTED",
                "ART_SPEC_CREATED",
                "RENDER_PLAN_CREATED",
            ],
            "privacy": {
                "publicSafe": True,
                "containsPII": False,
            },
        },
    }

    canonical = json.dumps(
        spec,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    spec["identityHash"] = (
        sha256_text(canonical)
    )

    return spec


def validate_batch(
    specs: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    names = [
        item["identity"]["canonicalName"]
        for item in specs
    ]

    dna_seeds = [
        item["dna"]["dnaSeedHash"]
        for item in specs
    ]

    resonances = [
        item["resonance"][
            "resonanceSignature"
        ]
        for item in specs
    ]

    abilities = [
        item["powers"][
            "signatureAbility"
        ]
        for item in specs
    ]

    if len(names) != len(set(names)):
        errors.append(
            "DUPLICATE_CANONICAL_NAME"
        )

    if len(dna_seeds) != len(
        set(dna_seeds)
    ):
        errors.append(
            "DUPLICATE_DNA_SEED_HASH"
        )

    if len(resonances) != len(
        set(resonances)
    ):
        errors.append(
            "DUPLICATE_RESONANCE_SIGNATURE"
        )

    if len(abilities) != len(
        set(abilities)
    ):
        errors.append(
            "DUPLICATE_SIGNATURE_ABILITY"
        )

    previous: list[dict[str, Any]] = []

    for spec in specs:
        token_id = (
            spec["identity"]["tokenId"]
        )

        coherence = (
            validate_coherence(spec)
        )

        for error in coherence:
            errors.append(
                f"TOKEN_{token_id:04d}:"
                f"{error}"
            )

        individuality = (
            validate_individuality(
                spec,
                previous,
                minimum_distance=4,
            )
        )

        for error in individuality:
            errors.append(
                f"TOKEN_{token_id:04d}:"
                f"{error}"
            )

        previous.append(spec)

    return errors


def write_batch() -> dict[str, Any]:
    SPEC_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROMPT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MANIFEST_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    specs = [
        build_spec(token_id)
        for token_id in range(1, 11)
    ]

    errors = validate_batch(
        specs
    )

    if errors:
        raise RuntimeError(
            "BATCH_VALIDATION_FAILED:\n"
            + "\n".join(errors)
        )

    token_records = []

    negative_prompt = (
        compile_negative_prompt()
    )

    for spec in specs:
        token_id = (
            spec["identity"]["tokenId"]
        )

        serial = f"{token_id:04d}"

        spec_path = (
            SPEC_DIR
            / f"{serial}.json"
        )

        prompt_path = (
            PROMPT_DIR
            / f"{serial}.txt"
        )

        spec_path.write_text(
            json.dumps(
                spec,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        positive_prompt = (
            compile_positive_prompt(
                spec
            )
        )

        prompt_path.write_text(
            "POSITIVE PROMPT\n"
            "===============\n"
            f"{positive_prompt}\n\n"
            "NEGATIVE PROMPT\n"
            "===============\n"
            f"{negative_prompt}\n",
            encoding="utf-8",
        )

        token_records.append(
            {
                "tokenId": token_id,
                "serial": (
                    spec["identity"][
                        "serial"
                    ]
                ),
                "canonicalName": (
                    spec["identity"][
                        "canonicalName"
                    ]
                ),
                "archetype": (
                    spec[
                        "classification"
                    ]["archetype"]
                ),
                "weaponType": (
                    spec[
                        "armorAndRelics"
                    ]["weaponType"]
                ),
                "signatureAbility": (
                    spec[
                        "powers"
                    ]["signatureAbility"]
                ),
                "resonanceSignature": (
                    spec[
                        "resonance"
                    ][
                        "resonanceSignature"
                    ]
                ),
                "dnaSeedHash": (
                    spec["dna"][
                        "dnaSeedHash"
                    ]
                ),
                "identityHash": (
                    spec[
                        "identityHash"
                    ]
                ),
                "specPath": str(
                    spec_path.relative_to(
                        ROOT
                    )
                ),
                "promptPath": str(
                    prompt_path.relative_to(
                        ROOT
                    )
                ),
            }
        )

    manifest = {
        "batchVersion": (
            "OX-GENESIS-BATCH-1"
        ),
        "batchId": BATCH_ID,
        "range": "#0001-#0010",
        "tier": "LEGENDARY",
        "cohort": "GENESIS",
        "era": "PRIMORDIAL_ORIGIN",
        "generationVersion": (
            GENERATION_VERSION
        ),
        "renderAuthorized": False,
        "canonicalizationAuthorized": (
            False
        ),
        "productionModel": (
            "UNASSIGNED"
        ),
        "tokensRequested": 10,
        "tokensGenerated": 10,
        "validationStatus": "PASS",
        "tokens": token_records,
    }

    canonical_manifest = (
        json.dumps(
            manifest,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    manifest["batchManifestHash"] = (
        sha256_text(
            canonical_manifest
        )
    )

    MANIFEST_PATH.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    manifest = write_batch()

    print(
        "GENESIS_BATCH_0001=PASS"
    )

    print(
        "TOKENS_GENERATED="
        f"{manifest['tokensGenerated']}"
    )

    print(
        "RANGE="
        f"{manifest['range']}"
    )

    print(
        "PRODUCTION_MODEL="
        f"{manifest['productionModel']}"
    )

    print(
        "RENDER_AUTHORIZED="
        f"{manifest['renderAuthorized']}"
    )

    print(
        "BATCH_MANIFEST_HASH="
        f"{manifest['batchManifestHash']}"
    )


if __name__ == "__main__":
    main()
