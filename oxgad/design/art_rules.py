"""OX-GAD PHASE 2C — versioned OriginX Art Rule Catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from oxgad.structure.canonical import (
    canonical_sha256,
)
from oxgad.structure.deterministic import (
    deterministic_choice,
)
from oxgad.structure.rules import (
    era_for_tier,
)


ART_RULE_CATALOG_VERSION = (
    "OX-ART-RULES-1"
)

DETAIL_PRIORITY = (
    "MACRO",
    "MESO",
    "MICRO",
)

UNIVERSE_ANCHORS = (
    "dark",
    "monumental",
    "ancient",
    "technological",
    "mysterious",
    "physically-heavy",
    "cinematic",
    "precise",
    "original",
)

FORBIDDEN_VISUAL_MODES = (
    "generic-fantasy",
    "generic-cyberpunk",
    "cartoon-styling",
    "recognizable-franchise-design",
    "excessive-neon",
    "flat-lighting",
    "random-ornament",
    "visual-noise",
    "watermark",
    "uncontrolled-text",
)

CONTINUITY_MOTIFS = (
    "megalithic-mass",
    "basaltic-foundation",
    "ancient-engineering",
    "controlled-energy-language",
    "material-weathering",
    "monumental-scale",
)


class ArtRuleError(
    ValueError
):
    """Raised when a canonical art rule cannot be resolved."""


@dataclass(
    frozen=True,
    slots=True,
)
class TierArtProfile:
    tier: str
    era: str
    evolution_rank: int

    body_mass: tuple[str, ...]
    silhouette_language: tuple[str, ...]
    head_language: tuple[str, ...]
    horn_language: tuple[str, ...]
    wing_language: tuple[str, ...]

    armor_language: tuple[str, ...]
    augmentation_language: tuple[str, ...]
    technology_language: tuple[str, ...]

    architecture_language: tuple[str, ...]
    atmosphere_language: tuple[str, ...]

    primary_materials: tuple[str, ...]
    secondary_materials: tuple[str, ...]
    accent_materials: tuple[str, ...]

    palette_language: tuple[str, ...]
    lighting_language: tuple[str, ...]

    composition_language: tuple[str, ...]
    camera_language: tuple[str, ...]

    macro_priorities: tuple[str, ...]
    meso_priorities: tuple[str, ...]
    micro_priorities: tuple[str, ...]


_PRIMITIVE = TierArtProfile(
    tier="RARE",
    era="Primitive Origin",
    evolution_rank=1,

    body_mass=(
        "massive-grounded",
        "dense-predatory",
        "ancient-heavy",
    ),
    silhouette_language=(
        "broad-megalithic",
        "low-centered-power",
        "weathered-apex-predator",
    ),
    head_language=(
        "stone-hewn-cranial-mass",
        "ancient-predatory-wedge",
        "heavy-basal-skull",
    ),
    horn_language=(
        "eroded-basalt-horns",
        "mineral-crusted-horns",
        "primitive-crown-horns",
    ),
    wing_language=(
        "massive-membranous",
        "scarred-structural",
        "ancient-ribbed",
    ),

    armor_language=(
        "natural-plate-dominant",
        "ritual-metal-reinforcement",
        "primitive-forged-segments",
    ),
    augmentation_language=(
        "minimal-ancient-inlay",
        "ritual-mechanical-graft",
        "dormant-relic-interface",
    ),
    technology_language=(
        "buried-ancient-machinery",
        "primitive-energy-conduit",
        "ritual-engineering",
    ),

    architecture_language=(
        "basalt-megalith",
        "cyclopean-stone-complex",
        "buried-monumental-ruin",
    ),
    atmosphere_language=(
        "mineral-dust",
        "volcanic-haze",
        "ancient-storm-pressure",
    ),

    primary_materials=(
        "obsidian",
        "basalt",
        "weathered-dark-stone",
    ),
    secondary_materials=(
        "oxidized-steel",
        "blackened-iron",
        "mineral-deposit",
    ),
    accent_materials=(
        "ember-mineral",
        "subsurface-amber",
        "dormant-energy-vein",
    ),

    palette_language=(
        "charcoal-basalt-ember",
        "obsidian-iron-amber",
        "black-stone-mineral-red",
    ),
    lighting_language=(
        "low-raking-monumental",
        "volumetric-ash-light",
        "subsurface-mineral-rim",
    ),

    composition_language=(
        "grounded-central-dominance",
        "low-angle-monumentality",
        "environmental-scale-contrast",
    ),
    camera_language=(
        "low-wide-heroic",
        "ground-level-cinematic",
        "measured-wide-perspective",
    ),

    macro_priorities=(
        "anatomy",
        "silhouette",
        "weight",
        "pose",
        "environment-scale",
    ),
    meso_priorities=(
        "scale-plates",
        "wing-structure",
        "horn-structure",
        "stone-architecture",
        "primitive-mechanics",
    ),
    micro_priorities=(
        "erosion",
        "fractures",
        "mineral-deposits",
        "surface-wear",
        "subsurface-glow",
    ),
)


_EVOLVED = TierArtProfile(
    tier="EPIC",
    era="Evolved Origin",
    evolution_rank=2,

    body_mass=(
        "massive-articulated",
        "dense-athletic",
        "monumental-mobile",
    ),
    silhouette_language=(
        "megalithic-articulated",
        "weaponized-elegance",
        "ancient-machine-predator",
    ),
    head_language=(
        "armored-cranial-geometry",
        "evolved-predatory-wedge",
        "integrated-relic-crown",
    ),
    horn_language=(
        "alloy-reinforced-horns",
        "segmented-mineral-horns",
        "engineered-crown-horns",
    ),
    wing_language=(
        "reinforced-membranous",
        "articulated-ribbed",
        "structural-alloy-wing",
    ),

    armor_language=(
        "integrated-dark-alloy",
        "layered-organic-mechanical",
        "articulated-relic-plate",
    ),
    augmentation_language=(
        "integrated-ancient-mechanics",
        "symbiotic-relic-interface",
        "controlled-energy-channel",
    ),
    technology_language=(
        "reactivated-ancient-machinery",
        "precision-energy-conduit",
        "megalithic-machine-system",
    ),

    architecture_language=(
        "machine-megalith",
        "basalt-alloy-cathedral",
        "reactivated-monumental-complex",
    ),
    atmosphere_language=(
        "charged-mineral-haze",
        "controlled-storm-field",
        "industrial-volumetric-depth",
    ),

    primary_materials=(
        "obsidian",
        "basalt",
        "dark-alloy",
    ),
    secondary_materials=(
        "oxidized-steel",
        "ceramic-metal-composite",
        "weathered-dark-alloy",
    ),
    accent_materials=(
        "controlled-energy-vein",
        "ionized-mineral",
        "subsurface-cyan-white",
    ),

    palette_language=(
        "graphite-basalt-cold-energy",
        "obsidian-alloy-white-blue",
        "dark-stone-steel-mineral-cyan",
    ),
    lighting_language=(
        "controlled-volumetric-rim",
        "architectural-energy-bounce",
        "high-contrast-relic-light",
    ),

    composition_language=(
        "structured-central-dominance",
        "monumental-diagonal-flow",
        "subject-environment-integration",
    ),
    camera_language=(
        "low-medium-cinematic",
        "architectural-wide-perspective",
        "controlled-heroic-perspective",
    ),

    macro_priorities=(
        "anatomy",
        "silhouette",
        "articulation",
        "pose",
        "environment-integration",
    ),
    meso_priorities=(
        "integrated-armor",
        "wing-articulation",
        "mechanical-regions",
        "machine-architecture",
        "energy-conduits",
    ),
    micro_priorities=(
        "controlled-weathering",
        "precision-fractures",
        "alloy-scratches",
        "mineral-interface",
        "energy-channel-detail",
    ),
)


_ASCENDED = TierArtProfile(
    tier="LEGENDARY",
    era="Ascended Origin",
    evolution_rank=3,

    body_mass=(
        "monumental-refined",
        "apex-architectonic",
        "massive-precise",
    ),
    silhouette_language=(
        "architectonic-apex",
        "monumental-transcendent",
        "ancient-precision-predator",
    ),
    head_language=(
        "architectonic-cranial-crown",
        "precision-apex-skull",
        "ascended-relic-geometry",
    ),
    horn_language=(
        "architectonic-horn-array",
        "precision-mineral-crown",
        "integrated-relic-horns",
    ),
    wing_language=(
        "monumental-engineered-wing",
        "precision-ribbed-wing",
        "integrated-ancient-flight-structure",
    ),

    armor_language=(
        "architectonic-dark-alloy",
        "seamless-organic-mechanical",
        "precision-relic-plate",
    ),
    augmentation_language=(
        "fully-integrated-ancient-system",
        "symbiotic-architectonic-interface",
        "precision-energy-topology",
    ),
    technology_language=(
        "ascended-ancient-engineering",
        "monumental-energy-network",
        "precision-megalithic-system",
    ),

    architecture_language=(
        "ascended-machine-megalith",
        "architectonic-basalt-citadel",
        "precision-monumental-sanctum",
    ),
    atmosphere_language=(
        "structured-energy-atmosphere",
        "monumental-volumetric-field",
        "controlled-ancient-aether",
    ),

    primary_materials=(
        "obsidian",
        "basalt",
        "precision-dark-alloy",
    ),
    secondary_materials=(
        "ceramic-metal-composite",
        "mineralized-alloy",
        "weathered-precision-metal",
    ),
    accent_materials=(
        "structured-energy-surface",
        "luminous-mineral-vein",
        "controlled-white-cyan-energy",
    ),

    palette_language=(
        "near-black-mineral-white-energy",
        "obsidian-precision-alloy-cyan-white",
        "basalt-graphite-mineral-light",
    ),
    lighting_language=(
        "architectonic-volumetric-light",
        "precision-energy-rim",
        "monumental-controlled-contrast",
    ),

    composition_language=(
        "architectonic-central-dominance",
        "monumental-layered-depth",
        "precision-subject-environment-unity",
    ),
    camera_language=(
        "monumental-low-perspective",
        "precision-wide-cinematic",
        "controlled-apex-perspective",
    ),

    macro_priorities=(
        "anatomy",
        "silhouette",
        "architectonic-form",
        "pose",
        "world-scale-coherence",
    ),
    meso_priorities=(
        "precision-armor",
        "wing-engineering",
        "integrated-systems",
        "architectonic-environment",
        "energy-topology",
    ),
    micro_priorities=(
        "precision-weathering",
        "controlled-microfracture",
        "material-interface",
        "mineral-growth",
        "subsurface-energy-detail",
    ),
)


_PROFILES = {
    _PRIMITIVE.tier: _PRIMITIVE,
    _EVOLVED.tier: _EVOLVED,
    _ASCENDED.tier: _ASCENDED,
}


def art_profile_for_tier(
    tier: str,
) -> TierArtProfile:
    try:
        profile = _PROFILES[tier]
    except KeyError as exc:
        raise ArtRuleError(
            f"Unsupported OriginX tier: {tier!r}."
        ) from exc

    canonical_era = era_for_tier(
        tier
    )

    if profile.era != canonical_era:
        raise ArtRuleError(
            "Art profile era is inconsistent with "
            "canonical Structure Engine rules."
        )

    return profile


def _choose(
    values: tuple[str, ...],
    *,
    seed: int,
    namespace: str,
) -> str:
    return deterministic_choice(
        values,
        seed=seed,
        namespace=(
            f"{ART_RULE_CATALOG_VERSION}."
            f"{namespace}"
        ),
    )


def select_art_rules(
    *,
    tier: str,
    seed: int,
) -> dict[str, Any]:
    """
    Resolve a deterministic art-rule bundle.

    This is not an image prompt and not an OX-ART-SPEC.
    It is structured source material for the Structure Engine.
    """

    profile = art_profile_for_tier(
        tier
    )

    return {
        "catalogVersion": ART_RULE_CATALOG_VERSION,
        "tier": profile.tier,
        "era": profile.era,
        "evolutionRank": profile.evolution_rank,
        "detailPriority": list(
            DETAIL_PRIORITY
        ),
        "universeAnchors": list(
            UNIVERSE_ANCHORS
        ),
        "continuityMotifs": list(
            CONTINUITY_MOTIFS
        ),
        "visualConstraints": {
            "forbiddenModes": list(
                FORBIDDEN_VISUAL_MODES
            ),
            "macroBeforeMeso": True,
            "mesoBeforeMicro": True,
            "microCannotMaskBadAnatomy": True,
        },
        "dragon": {
            "bodyMass": _choose(
                profile.body_mass,
                seed=seed,
                namespace="dragon.body_mass",
            ),
            "silhouette": _choose(
                profile.silhouette_language,
                seed=seed,
                namespace="dragon.silhouette",
            ),
            "head": _choose(
                profile.head_language,
                seed=seed,
                namespace="dragon.head",
            ),
            "horns": _choose(
                profile.horn_language,
                seed=seed,
                namespace="dragon.horns",
            ),
            "wings": _choose(
                profile.wing_language,
                seed=seed,
                namespace="dragon.wings",
            ),
            "armor": _choose(
                profile.armor_language,
                seed=seed,
                namespace="dragon.armor",
            ),
            "augmentation": _choose(
                profile.augmentation_language,
                seed=seed,
                namespace="dragon.augmentation",
            ),
        },
        "technology": {
            "language": _choose(
                profile.technology_language,
                seed=seed,
                namespace="technology.language",
            ),
        },
        "environment": {
            "architecture": _choose(
                profile.architecture_language,
                seed=seed,
                namespace="environment.architecture",
            ),
            "atmosphere": _choose(
                profile.atmosphere_language,
                seed=seed,
                namespace="environment.atmosphere",
            ),
        },
        "materials": {
            "primary": _choose(
                profile.primary_materials,
                seed=seed,
                namespace="materials.primary",
            ),
            "secondary": _choose(
                profile.secondary_materials,
                seed=seed,
                namespace="materials.secondary",
            ),
            "accent": _choose(
                profile.accent_materials,
                seed=seed,
                namespace="materials.accent",
            ),
        },
        "color": {
            "palette": _choose(
                profile.palette_language,
                seed=seed,
                namespace="color.palette",
            ),
        },
        "lighting": {
            "language": _choose(
                profile.lighting_language,
                seed=seed,
                namespace="lighting.language",
            ),
        },
        "composition": {
            "language": _choose(
                profile.composition_language,
                seed=seed,
                namespace="composition.language",
            ),
            "camera": _choose(
                profile.camera_language,
                seed=seed,
                namespace="composition.camera",
            ),
        },
        "detail": {
            "macro": list(
                profile.macro_priorities
            ),
            "meso": list(
                profile.meso_priorities
            ),
            "micro": list(
                profile.micro_priorities
            ),
        },
    }


def art_rule_hash(
    *,
    tier: str,
    seed: int,
) -> str:
    return canonical_sha256(
        select_art_rules(
            tier=tier,
            seed=seed,
        )
    )
