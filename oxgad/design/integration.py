"""Canonical integration of OriginX Art Rules and Art Design Grammar."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from oxgad.design.art_rules import (
    ART_RULE_CATALOG_VERSION,
    art_rule_hash,
    select_art_rules,
)
from oxgad.design.grammar import (
    ART_DESIGN_GRAMMAR_VERSION,
    compile_art_design_grammar,
    validate_art_design_grammar,
)
from oxgad.structure.canonical import canonical_sha256


ART_DESIGN_INTEGRATION_VERSION = (
    "OX-ART-DESIGN-INTEGRATION-1"
)


class ArtDesignIntegrationError(ValueError):
    """Raised when an integrated design contract is invalid."""


def _validate_seed(seed: int) -> None:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ArtDesignIntegrationError(
            "seed must be an integer"
        )

    if seed < 0:
        raise ArtDesignIntegrationError(
            "seed must be non-negative"
        )


def _integrated_payload(
    *,
    tier: str,
    seed: int,
) -> dict[str, Any]:
    _validate_seed(seed)

    art_rules = select_art_rules(
        tier=tier,
        seed=seed,
    )

    grammar = compile_art_design_grammar(tier)
    validate_art_design_grammar(grammar)

    if art_rules["tier"] != grammar["tier"]:
        raise ArtDesignIntegrationError(
            "art rule tier and grammar tier disagree"
        )

    if art_rules["era"] != grammar["era"]:
        raise ArtDesignIntegrationError(
            "art rule era and grammar era disagree"
        )

    if (
        art_rules["evolutionRank"]
        != grammar["evolutionRank"]
    ):
        raise ArtDesignIntegrationError(
            "art rule and grammar evolution ranks disagree"
        )

    if (
        art_rules["detailPriority"]
        != grammar["invariants"]["detailAuthority"]
    ):
        raise ArtDesignIntegrationError(
            "detail authority contracts disagree"
        )

    return {
        "integrationVersion": (
            ART_DESIGN_INTEGRATION_VERSION
        ),
        "catalogVersion": ART_RULE_CATALOG_VERSION,
        "grammarVersion": ART_DESIGN_GRAMMAR_VERSION,
        "tier": tier,
        "era": art_rules["era"],
        "evolutionRank": art_rules["evolutionRank"],
        "seed": seed,
        "artRuleHash": art_rule_hash(
            tier=tier,
            seed=seed,
        ),
        "artRules": art_rules,
        "grammar": grammar,
        "integrationInvariants": {
            "tierAgreement": True,
            "eraAgreement": True,
            "evolutionRankAgreement": True,
            "detailAuthorityAgreement": True,
            "providerIndependent": True,
            "renderIndependent": True,
        },
    }


def integrated_design_hash(
    *,
    tier: str,
    seed: int,
) -> str:
    """Hash the integrated design payload, excluding its own hash."""

    return canonical_sha256(
        _integrated_payload(
            tier=tier,
            seed=seed,
        )
    )


def compile_integrated_design(
    *,
    tier: str,
    seed: int,
) -> dict[str, Any]:
    """Compile deterministic structured design authority."""

    payload = _integrated_payload(
        tier=tier,
        seed=seed,
    )

    contract = {
        **payload,
        "designHash": canonical_sha256(payload),
    }

    validate_integrated_design(contract)
    return deepcopy(contract)


def validate_integrated_design(
    design: dict[str, Any],
) -> None:
    if not isinstance(design, dict):
        raise ArtDesignIntegrationError(
            "integrated design must be a mapping"
        )

    required = {
        "integrationVersion",
        "catalogVersion",
        "grammarVersion",
        "tier",
        "era",
        "evolutionRank",
        "seed",
        "artRuleHash",
        "artRules",
        "grammar",
        "integrationInvariants",
        "designHash",
    }

    if set(design) != required:
        raise ArtDesignIntegrationError(
            "integrated design fields do not match contract"
        )

    if (
        design["integrationVersion"]
        != ART_DESIGN_INTEGRATION_VERSION
    ):
        raise ArtDesignIntegrationError(
            "invalid integration version"
        )

    tier = design["tier"]
    seed = design["seed"]
    _validate_seed(seed)

    expected = _integrated_payload(
        tier=tier,
        seed=seed,
    )

    actual_payload = {
        key: value
        for key, value in design.items()
        if key != "designHash"
    }

    if actual_payload != expected:
        raise ArtDesignIntegrationError(
            "integrated design does not match canonical sources"
        )

    expected_hash = canonical_sha256(expected)

    if design["designHash"] != expected_hash:
        raise ArtDesignIntegrationError(
            "designHash does not match canonical payload"
        )


__all__ = (
    "ART_DESIGN_INTEGRATION_VERSION",
    "ArtDesignIntegrationError",
    "compile_integrated_design",
    "integrated_design_hash",
    "validate_integrated_design",
)
