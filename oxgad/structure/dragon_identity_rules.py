from __future__ import annotations

from typing import Any


RULE_VERSION = "OX-DRAGON-RULES-1"


def validate_coherence(
    spec: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    classification = spec.get(
        "classification",
        {},
    )

    armor = spec.get(
        "armorAndRelics",
        {},
    )

    powers = spec.get(
        "powers",
        {},
    )

    archetype = classification.get(
        "archetype"
    )

    combat_role = classification.get(
        "combatRole"
    )

    weapon = armor.get(
        "weaponType",
        "NONE",
    )

    ability = powers.get(
        "signatureAbility"
    )

    if archetype == "ORACLE":
        if weapon not in {
            "NONE",
            "RITUAL_STAFF",
        }:
            errors.append(
                "ORACLE_WEAPON_INCOHERENT"
            )

    if archetype == "EXECUTIONER":
        if weapon not in {
            "CHAINED_GREATSWORD",
            "OBSIDIAN_HALBERD",
            "TAIL_BLADE",
        }:
            errors.append(
                "EXECUTIONER_WEAPON_INCOHERENT"
            )

        if combat_role not in {
            "EXECUTIONER_MONARCH",
            "FRONTLINE_DESTROYER",
        }:
            errors.append(
                "EXECUTIONER_ROLE_INCOHERENT"
            )

    if archetype == "STORM_TYRANT":
        if ability not in {
            "THUNDER_RESONANCE",
            "STORM_SUMMONING",
        }:
            errors.append(
                "STORM_TYRANT_POWER_INCOHERENT"
            )

    if weapon == "NONE":
        expression = powers.get(
            "powerExpression",
            [],
        )

        if not expression:
            errors.append(
                "WEAPONLESS_REQUIRES_POWER_EXPRESSION"
            )

    return errors


def identity_signature(
    spec: dict[str, Any],
) -> tuple[str, ...]:
    identity = spec.get(
        "identity",
        {},
    )

    classification = spec.get(
        "classification",
        {},
    )

    anatomy = spec.get(
        "anatomy",
        {},
    )

    armor = spec.get(
        "armorAndRelics",
        {},
    )

    powers = spec.get(
        "powers",
        {},
    )

    resonance = spec.get(
        "resonance",
        {},
    )

    return (
        str(identity.get("canonicalName")),
        str(classification.get("archetype")),
        str(classification.get("temperament")),
        str(classification.get("combatRole")),
        str(anatomy.get("silhouetteProfile")),
        str(armor.get("weaponType")),
        str(powers.get("signatureAbility")),
        str(resonance.get("resonanceClass")),
    )


def individuality_distance(
    left: dict[str, Any],
    right: dict[str, Any],
) -> int:
    a = identity_signature(left)
    b = identity_signature(right)

    return sum(
        1
        for x, y in zip(a, b)
        if x != y
    )


def validate_individuality(
    candidate: dict[str, Any],
    previous: list[dict[str, Any]],
    minimum_distance: int = 4,
) -> list[str]:
    errors: list[str] = []

    for other in previous:
        distance = individuality_distance(
            candidate,
            other,
        )

        if distance < minimum_distance:
            other_id = (
                other
                .get("identity", {})
                .get("tokenId", "UNKNOWN")
            )

            errors.append(
                "INSUFFICIENT_INDIVIDUALITY:"
                f"{other_id}:"
                f"{distance}"
            )

    return errors
