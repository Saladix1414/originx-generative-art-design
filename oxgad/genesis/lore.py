"""Deterministic Resonance, Glyph and Akashic records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.genesis.identity import build_genesis_identity
from oxgad.structure.canonical import (
    canonical_json,
    canonical_sha256,
)


GENESIS_LORE_VERSION = "OX-GENESIS-LORE-1"
RESONANCE_VERSION = "OX-RESONANCE-1"
GLYPH_VERSION = "OX-RESONANCE-GLYPH-1"
AKASHIC_VERSION = "OX-AKASHIC-1"

GENESIS_LORE_SCHEMA_PATH = Path(
    "schemas/ox-genesis-lore-1.schema.json"
)

_RESONANCE_CLASSES = (
    "MONOLITHIC",
    "ABYSSAL",
    "FORGEBOUND",
    "TEMPEST",
    "CHTHONIC",
)

_SPECTRA = (
    ("deep-cyan", "obsidian-black", "mineral-white"),
    ("restrained-crimson", "basalt-grey", "ash-white"),
    ("cold-cyan", "dark-forged-metal", "ember-red"),
    ("storm-blue", "obsidian", "restrained-crimson"),
    ("mineral-cyan", "weathered-stone", "deep-black"),
)

_FORBIDDEN_KEYS = {
    "email",
    "buyeremail",
    "realname",
    "fullname",
    "privateorderid",
    "paymentid",
    "authtoken",
    "password",
    "secret",
    "privatesignature",
}


def validate_genesis_lore(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        GENESIS_LORE_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def _digest_bytes(value: Mapping[str, Any]) -> bytes:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).digest()


def _assert_public_safe(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).replace("_", "").lower()

            if normalized in _FORBIDDEN_KEYS:
                raise ValueError(
                    f"Private field forbidden in Akashic payload: {key}"
                )

            _assert_public_safe(item)

    elif isinstance(value, list):
        for item in value:
            _assert_public_safe(item)


def build_resonance(
    identity: Mapping[str, Any],
) -> dict[str, Any]:
    material = {
        "tokenId": identity["tokenId"],
        "canonicalName": identity["canonicalName"],
        "dnaHash": identity["dnaHash"],
        "seedHash": identity["seedHash"],
        "version": RESONANCE_VERSION,
    }
    digest = _digest_bytes(material)
    index = identity["tokenId"] - 1
    primary = 100 + int.from_bytes(digest[0:2], "big") % 900
    secondary = 100 + int.from_bytes(digest[2:4], "big") % 900
    pulse = 1 + digest[4] % 12
    phase = int.from_bytes(digest[5:7], "big") % 360
    glyph_seed = int.from_bytes(digest[8:16], "big")

    payload = {
        "resonanceVersion": RESONANCE_VERSION,
        "resonanceId": (
            f"OX-RES-GENESIS-{identity['tokenId']:04d}"
        ),
        "resonanceClass": _RESONANCE_CLASSES[index % 5],
        "spectrum": list(_SPECTRA[index % 5]),
        "primaryFrequency": primary,
        "secondaryFrequency": secondary,
        "pulse": pulse,
        "phaseDegrees": phase,
        "glyphSeed": glyph_seed,
        "interpretation": (
            "Deterministic artistic and mathematical parameters; "
            "not a claim of spiritual, physical, or scientific energy."
        ),
    }

    payload["resonanceSignature"] = canonical_sha256(
        payload
    )
    return payload


def build_glyph(
    identity: Mapping[str, Any],
    resonance: Mapping[str, Any],
) -> dict[str, Any]:
    seed = resonance["glyphSeed"]
    spokes = 5 + seed % 7
    rings = 2 + (seed // 7) % 4
    rotation = resonance["phaseDegrees"]
    asymmetry = (seed // 31) % 5

    geometry = {
        "spokes": spokes,
        "rings": rings,
        "rotationDegrees": rotation,
        "asymmetryIndex": asymmetry,
        "influenceTargets": [
            "horn rhythm",
            "wing geometry",
            "energy topology",
            "cracks",
            "engravings",
            "architecture",
            "lighting patterns",
        ],
    }

    lines = []
    for index in range(spokes):
        angle = (rotation + index * (360 / spokes)) % 360
        lines.append(
            f'<line x1="128" y1="128" x2="128" y2="24" '
            f'transform="rotate({angle:.3f} 128 128)"/>'
        )

    circles = [
        f'<circle cx="128" cy="128" r="{24 + ring * 20}"/>'
        for ring in range(1, rings + 1)
    ]

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 256 256" fill="none" '
        'stroke="currentColor" stroke-width="3">'
        + "".join(circles)
        + "".join(lines)
        + "</svg>"
    )

    svg_hash = (
        "sha256:"
        + hashlib.sha256(svg.encode("utf-8")).hexdigest()
    )

    manifest = {
        "glyphVersion": GLYPH_VERSION,
        "tokenId": identity["tokenId"],
        "glyphSeed": seed,
        "geometry": geometry,
        "svgHash": svg_hash,
        "watermarkRequired": False,
    }

    return {
        **manifest,
        "svg": svg,
        "manifestHash": canonical_sha256(manifest),
    }


def _akashic_event(
    *,
    token_id: int,
    sequence: int,
    event_type: str,
    previous_hash: str | None,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    _assert_public_safe(payload)

    body = {
        "sequence": sequence,
        "eventType": event_type,
        "lifecycleReference": (
            f"GENESIS-{token_id:04d}-EVENT-{sequence:04d}"
        ),
        "previousEventHash": previous_hash,
        "payload": dict(payload),
        "publicSafe": True,
        "containsPII": False,
    }

    return {
        **body,
        "eventHash": canonical_sha256(body),
    }


def build_initial_akashic(
    identity: Mapping[str, Any],
    resonance: Mapping[str, Any],
    glyph: Mapping[str, Any],
) -> dict[str, Any]:
    specifications = (
        (
            "DNA_FORGED",
            {"dnaHash": identity["dnaHash"]},
        ),
        (
            "NAME_ASSIGNED",
            {
                "canonicalName": identity["canonicalName"],
                "title": identity["title"],
            },
        ),
        (
            "RESONANCE_CREATED",
            {
                "resonanceId": resonance["resonanceId"],
                "resonanceSignature": (
                    resonance["resonanceSignature"]
                ),
            },
        ),
        (
            "RESONANCE_GLYPH_MANIFESTED",
            {
                "svgHash": glyph["svgHash"],
                "manifestHash": glyph["manifestHash"],
            },
        ),
    )

    events = []
    previous = None

    for sequence, (event_type, payload) in enumerate(
        specifications,
        start=1,
    ):
        event = _akashic_event(
            token_id=identity["tokenId"],
            sequence=sequence,
            event_type=event_type,
            previous_hash=previous,
            payload=payload,
        )
        events.append(event)
        previous = event["eventHash"]

    return {
        "akashicVersion": AKASHIC_VERSION,
        "tokenId": identity["tokenId"],
        "appendOnly": True,
        "tamperEvident": True,
        "events": events,
        "headHash": previous,
    }


def verify_akashic_chain(
    value: Mapping[str, Any],
) -> bool:
    previous = None

    for expected_sequence, event in enumerate(
        value["events"],
        start=1,
    ):
        if event["sequence"] != expected_sequence:
            return False

        if event["previousEventHash"] != previous:
            return False

        body = {
            key: item
            for key, item in event.items()
            if key != "eventHash"
        }

        if canonical_sha256(body) != event["eventHash"]:
            return False

        try:
            _assert_public_safe(event["payload"])
        except ValueError:
            return False

        previous = event["eventHash"]

    return value["headHash"] == previous


def build_genesis_lore(token_id: int) -> dict[str, Any]:
    identity = build_genesis_identity(token_id)
    resonance = build_resonance(identity)
    glyph = build_glyph(identity, resonance)
    akashic = build_initial_akashic(
        identity,
        resonance,
        glyph,
    )

    payload = {
        "loreVersion": GENESIS_LORE_VERSION,
        "tokenId": token_id,
        "resonance": resonance,
        "glyph": glyph,
        "akashic": akashic,
    }

    value = {
        **payload,
        "packageHash": canonical_sha256(payload),
    }

    validate_genesis_lore(value)

    if not verify_akashic_chain(akashic):
        raise RuntimeError("Invalid initial Akashic chain.")

    return value


def build_genesis_batch_lore() -> tuple[dict[str, Any], ...]:
    values = tuple(
        build_genesis_lore(token_id)
        for token_id in range(1, 11)
    )

    signatures = {
        item["resonance"]["resonanceSignature"]
        for item in values
    }
    glyph_hashes = {
        item["glyph"]["svgHash"]
        for item in values
    }

    if len(signatures) != 10:
        raise RuntimeError("Duplicate Resonance signature.")

    if len(glyph_hashes) != 10:
        raise RuntimeError("Duplicate Glyph.")

    return values
