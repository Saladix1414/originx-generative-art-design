"""Formal provider-independent Art Design Grammar for OriginX."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from oxgad.design.art_rules import art_profile_for_tier


ART_DESIGN_GRAMMAR_VERSION = "OX-ART-GRAMMAR-1"

DETAIL_AUTHORITY = ("MACRO", "MESO", "MICRO")

DOMAIN_ORDER = (
    "morphology",
    "anatomy",
    "materials",
    "technology",
    "augmentation",
    "architecture",
    "lighting",
    "atmosphere",
    "weathering",
    "ornament",
    "damage",
)


class ArtDesignGrammarError(ValueError):
    """Raised when an Art Design Grammar contract is invalid."""


_TIER_GRAMMAR: dict[str, dict[str, tuple[int, str]]] = {
    "RARE": {
        "morphology": (1, "foundational-megalithic"),
        "anatomy": (1, "mass-first-predatory"),
        "materials": (1, "weathered-foundational"),
        "technology": (1, "buried-ritual-engineering"),
        "augmentation": (1, "sparse-integrated"),
        "architecture": (1, "cyclopean-foundation"),
        "lighting": (1, "low-raking-monumental"),
        "atmosphere": (1, "ash-mineral-depth"),
        "weathering": (3, "ancient-heavy"),
        "ornament": (1, "restrained-ritual"),
        "damage": (3, "age-borne"),
    },
    "EPIC": {
        "morphology": (2, "articulated-megalithic"),
        "anatomy": (2, "mobile-structural-power"),
        "materials": (2, "alloy-integrated"),
        "technology": (2, "reactivated-precision-engineering"),
        "augmentation": (2, "functional-integrated"),
        "architecture": (2, "machine-megalithic"),
        "lighting": (2, "controlled-energy-contrast"),
        "atmosphere": (2, "reactivated-volumetric-depth"),
        "weathering": (2, "controlled-ancient"),
        "ornament": (2, "structural-symbolic"),
        "damage": (2, "preserved-conflict"),
    },
    "LEGENDARY": {
        "morphology": (3, "architectonic-apex"),
        "anatomy": (3, "precision-monumental"),
        "materials": (3, "precision-relic-composite"),
        "technology": (3, "ascended-ancient-engineering"),
        "augmentation": (3, "seamless-architectonic"),
        "architecture": (3, "precision-monumental-sanctum"),
        "lighting": (3, "architectonic-controlled-contrast"),
        "atmosphere": (3, "structured-energy-depth"),
        "weathering": (1, "precision-preserved"),
        "ornament": (2, "restrained-sovereign"),
        "damage": (1, "minimal-ancestral"),
    },
}


def _catalog_snapshot(tier: str) -> dict[str, Any]:
    profile = art_profile_for_tier(tier)

    return {
        "bodyMass": list(profile.body_mass),
        "silhouette": list(profile.silhouette_language),
        "armor": list(profile.armor_language),
        "technology": list(profile.technology_language),
        "augmentation": list(profile.augmentation_language),
        "architecture": list(profile.architecture_language),
        "atmosphere": list(profile.atmosphere_language),
        "materials": {
            "primary": list(profile.primary_materials),
            "secondary": list(profile.secondary_materials),
            "accent": list(profile.accent_materials),
        },
        "lighting": list(profile.lighting_language),
    }


def validate_art_design_grammar(grammar: dict[str, Any]) -> None:
    if grammar.get("grammarVersion") != ART_DESIGN_GRAMMAR_VERSION:
        raise ArtDesignGrammarError("invalid grammar version")

    domains = grammar.get("domains")

    if not isinstance(domains, dict):
        raise ArtDesignGrammarError("domains must be a mapping")

    if tuple(domains) != DOMAIN_ORDER:
        raise ArtDesignGrammarError("grammar domain order mismatch")

    for domain, rule in domains.items():
        intensity = rule.get("intensity")
        mode = rule.get("mode")

        if intensity not in (1, 2, 3):
            raise ArtDesignGrammarError(
                f"{domain} intensity must be 1, 2 or 3"
            )

        if not isinstance(mode, str) or not mode:
            raise ArtDesignGrammarError(
                f"{domain} mode must be non-empty"
            )

    invariants = grammar.get("invariants", {})

    if tuple(invariants.get("detailAuthority", ())) != DETAIL_AUTHORITY:
        raise ArtDesignGrammarError("detail authority violated")


def compile_art_design_grammar(tier: str) -> dict[str, Any]:
    if tier not in _TIER_GRAMMAR:
        raise ArtDesignGrammarError(f"unsupported tier: {tier}")

    profile = art_profile_for_tier(tier)

    domains = {
        name: {
            "intensity": intensity,
            "mode": mode,
        }
        for name, (intensity, mode) in _TIER_GRAMMAR[tier].items()
    }

    grammar = {
        "grammarVersion": ART_DESIGN_GRAMMAR_VERSION,
        "tier": tier,
        "era": profile.era,
        "evolutionRank": profile.evolution_rank,
        "domainOrder": list(DOMAIN_ORDER),
        "domains": domains,
        "catalog": _catalog_snapshot(tier),
        "invariants": {
            "detailAuthority": list(DETAIL_AUTHORITY),
            "anatomyBeforeDetail": True,
            "structuralEvolutionNotBrightness": True,
            "randomOrnamentForbidden": True,
            "providerIndependent": True,
        },
    }

    validate_art_design_grammar(grammar)
    return deepcopy(grammar)


__all__ = (
    "ART_DESIGN_GRAMMAR_VERSION",
    "DETAIL_AUTHORITY",
    "DOMAIN_ORDER",
    "ArtDesignGrammarError",
    "compile_art_design_grammar",
    "validate_art_design_grammar",
)
