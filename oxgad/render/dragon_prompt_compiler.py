from __future__ import annotations

from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

NEGATIVE_PROMPT_PATH = (
    ROOT
    / "config"
    / "dragon_negative_prompt_v1.txt"
)


def readable(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(
            readable(item)
            for item in value
        )

    if value is None:
        return "none"

    return str(value).replace(
        "_",
        " ",
    ).lower()


def compile_positive_prompt(
    spec: dict[str, Any],
) -> str:

    i = spec["identity"]
    c = spec["classification"]
    a = spec["anatomy"]
    m = spec["materials"]
    r = spec["armorAndRelics"]
    p = spec["powers"]
    res = spec["resonance"]
    g = spec["glyph"]
    e = spec["environment"]
    comp = spec["composition"]
    light = spec["lighting"]

    parts = [
        "Original OriginX dragon NFT artwork.",
        (
            f"{readable(i['tier'])} "
            f"{readable(i['cohort'])} entity "
            f"from the {readable(i['era'])} era."
        ),
        (
            f"Identity: {i['canonicalName']}, "
            f"{i['title']}."
        ),
        (
            f"Archetype: {readable(c['archetype'])}; "
            f"temperament: {readable(c['temperament'])}; "
            f"presence: {readable(c['presence'])}; "
            f"combat role: {readable(c['combatRole'])}."
        ),
        (
            "Anatomy: "
            f"{readable(a['bodyStructure'])}, "
            f"{readable(a['headStyle'])}, "
            f"{readable(a['hornStyle'])}, "
            f"{readable(a['wingStyle'])}, "
            f"{readable(a['tailStyle'])}, "
            f"{readable(a['silhouetteProfile'])}."
        ),
        (
            "Materials: "
            f"{readable(m['primaryMaterial'])}, "
            f"{readable(m['secondaryMaterial'])}, "
            f"{readable(m.get('tertiaryMaterial'))}, "
            f"{readable(m['surfaceAge'])}, "
            f"{readable(m['damageProfile'])}."
        ),
        (
            "Weapon or relic: "
            f"{readable(r.get('weaponType'))}, "
            f"{readable(r.get('weaponMaterial'))}, "
            f"{readable(r.get('relicType'))}."
        ),
        (
            "Signature power: "
            f"{readable(p['signatureAbility'])}; "
            f"{readable(p['energyMode'])}; "
            f"{readable(p['powerExpression'])}."
        ),
        (
            "Resonance: "
            f"{readable(res['resonanceClass'])}, "
            f"{readable(res['spectrum'])}; "
            f"glyph influence: "
            f"{readable(g['influenceAreas'])}."
        ),
        (
            "Environment: "
            f"{readable(e['setting'])}, "
            f"{readable(e['architecture'])}, "
            f"{readable(e['weather'])}, "
            f"{readable(e['atmosphere'])}."
        ),
        (
            "Composition: "
            f"{readable(comp['cameraAngle'])}, "
            f"{readable(comp['framing'])}, "
            f"{readable(comp['pose'])}, "
            f"{readable(comp['storyBeat'])}."
        ),
        (
            "Lighting: "
            f"{readable(light['keyLight'])}, "
            f"{readable(light['rimLight'])}, "
            f"{readable(light['accentLight'])}, "
            f"{readable(light['contrastLevel'])}."
        ),
        (
            "High-end dark monumental cinematic "
            "concept art, believable anatomy, "
            "strong silhouette, rich material detail, "
            "extreme individual identity, original design."
        ),
    ]

    return " ".join(parts)


def compile_negative_prompt() -> str:
    return (
        NEGATIVE_PROMPT_PATH
        .read_text(
            encoding="utf-8"
        )
        .strip()
    )
