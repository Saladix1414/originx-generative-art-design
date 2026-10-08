"""OX-GAD PHASE 2B — versioned Structure Engine rules."""

from __future__ import annotations

from dataclasses import dataclass


STRUCTURE_RULESET_VERSION = (
    "OX-STRUCTURE-RULES-1"
)


class StructureRuleError(
    ValueError
):
    """Raised when no canonical structure rule exists."""


@dataclass(
    frozen=True,
    slots=True,
)
class TierRule:
    tier: str
    era: str


_TIER_RULES = {
    "RARE": TierRule(
        tier="RARE",
        era="Primitive Origin",
    ),
    "EPIC": TierRule(
        tier="EPIC",
        era="Evolved Origin",
    ),
    "LEGENDARY": TierRule(
        tier="LEGENDARY",
        era="Ascended Origin",
    ),
}


def tier_rule(
    tier: str,
) -> TierRule:
    try:
        return _TIER_RULES[tier]
    except KeyError as exc:
        raise StructureRuleError(
            f"Unsupported OriginX tier: {tier!r}."
        ) from exc


def era_for_tier(
    tier: str,
) -> str:
    return tier_rule(
        tier
    ).era
