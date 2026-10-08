"""OX-GAD PHASE 2E — first 10 deterministic Art Specs."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from oxgad import ART_SPEC_VERSION
from oxgad.design.art_rules import (
    ART_RULE_CATALOG_VERSION,
)
from oxgad.structure.assembler import (
    STRUCTURE_ASSEMBLER_VERSION,
    ArtSpecAssembly,
    assemble_art_spec,
)
from oxgad.structure.canonical import (
    canonical_json,
    canonical_sha256,
)
from oxgad.structure.input import (
    StructureInput,
)
from oxgad.structure.validator import (
    validate_art_spec,
)


FIRST10_MANIFEST_VERSION = (
    "OX-FIRST10-MANIFEST-1"
)

FIRST10_COUNT = 10

_NAMES = (
    "Vaerkaion",
    "Kaeloryx",
    "Dravethar",
    "Oryndrax",
    "Zhaerion",
    "Velkaryn",
    "Tharvexis",
    "Nyxaroth",
    "Korvaelis",
    "Aerzathen",
)

_ARCHETYPES = (
    "ancient-dragon",
    "basalt-wyrm",
    "megalithic-drake",
    "obsidian-guardian",
    "mineral-titan",
)

_BODY_MASS = (
    "heavy",
    "massive",
    "dense",
    "broad",
    "monumental",
)

_POSTURES = (
    "grounded",
    "watchful",
    "braced",
    "ascending",
    "coiled",
)

_HORNS = (
    "forward-crown",
    "swept-crown",
    "basalt-ridge",
    "split-crown",
    "mineral-array",
)

_WINGS = (
    "broad-ribbed",
    "heavy-membranous",
    "scarred-structural",
    "long-ribbed",
    "compact-power",
)

_MARKINGS = (
    "fractured-runes",
    "mineral-lines",
    "basalt-veins",
    "ritual-scars",
    "subsurface-glyphs",
)

_RESONANCE = (
    "ember",
    "mineral-red",
    "amber",
    "deep-cyan",
    "white-ash",
)


def first_10_packages() -> tuple[dict[str, Any], ...]:
    packages: list[dict[str, Any]] = []

    for index in range(FIRST10_COUNT):
        token_id = index + 1

        dna = {
            "archetype": _ARCHETYPES[
                index % len(_ARCHETYPES)
            ],
            "body": {
                "mass": _BODY_MASS[
                    index % len(_BODY_MASS)
                ],
                "posture": _POSTURES[
                    index % len(_POSTURES)
                ],
            },
            "horns": {
                "geometry": _HORNS[
                    index % len(_HORNS)
                ],
            },
            "wings": {
                "structure": _WINGS[
                    index % len(_WINGS)
                ],
            },
            "markings": {
                "language": _MARKINGS[
                    index % len(_MARKINGS)
                ],
            },
            "lineage": {
                "generation": 1,
                "collection": "Founding-6000",
                "cohort": "RARE",
                "index": token_id,
            },
        }

        dna_hash = canonical_sha256(
            dna
        )

        resonance = {
            "spectrum": _RESONANCE[
                index % len(_RESONANCE)
            ],
            "energyTopology": (
                "radial"
                if index % 2 == 0
                else "axial"
            ),
            "intensity": round(
                0.30
                + (index * 0.05),
                2,
            ),
            "narrativeRole": (
                "visual influence only"
            ),
        }

        packages.append(
            {
                "tokenId": token_id,
                "serial": f"#{token_id:04d}",
                "canonicalName": _NAMES[index],
                "tier": "RARE",
                "generationTheme": (
                    "Primitive Origin"
                ),
                "dna": dna,
                "dnaHash": dna_hash,
                "resonance": resonance,
            }
        )

    return tuple(
        packages
    )


def generate_first_10() -> tuple[
    ArtSpecAssembly,
    ...,
]:
    results: list[
        ArtSpecAssembly
    ] = []

    for package in first_10_packages():
        structure_input = (
            StructureInput.from_mapping(
                package
            )
        )

        result = assemble_art_spec(
            structure_input
        )

        validate_art_spec(
            result.art_spec
        )

        results.append(
            result
        )

    return tuple(
        results
    )


def build_manifest(
    results: tuple[
        ArtSpecAssembly,
        ...,
    ],
) -> dict[str, Any]:
    if len(results) != FIRST10_COUNT:
        raise ValueError(
            "First-10 manifest requires "
            f"exactly {FIRST10_COUNT} Art Specs."
        )

    entries = []

    for result in results:
        identity = result.art_spec[
            "identity"
        ]

        token_id = identity[
            "tokenId"
        ]

        entries.append(
            {
                "tokenId": token_id,
                "serial": identity["serial"],
                "canonicalName": identity[
                    "canonicalName"
                ],
                "tier": identity["tier"],
                "era": identity["era"],
                "seed": result.seed,
                "dnaHash": identity[
                    "dnaHash"
                ],
                "artRuleHash": (
                    result.art_rule_hash
                ),
                "artSpecHash": (
                    result.art_spec_hash
                ),
                "file": (
                    f"token-{token_id:04d}.json"
                ),
            }
        )

    return {
        "manifestVersion": (
            FIRST10_MANIFEST_VERSION
        ),
        "artSpecVersion": (
            ART_SPEC_VERSION
        ),
        "assemblerVersion": (
            STRUCTURE_ASSEMBLER_VERSION
        ),
        "artRuleCatalogVersion": (
            ART_RULE_CATALOG_VERSION
        ),
        "count": FIRST10_COUNT,
        "tier": "RARE",
        "era": "Primitive Origin",
        "entries": entries,
    }


def _atomic_write(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    temporary.write_text(
        content,
        encoding="utf-8",
    )

    temporary.replace(
        path
    )


def write_first_10(
    output_dir: Path,
) -> dict[str, Any]:
    results = generate_first_10()

    art_spec_hashes: set[str] = set()

    for result in results:
        identity = result.art_spec[
            "identity"
        ]

        token_id = identity[
            "tokenId"
        ]

        path = (
            output_dir
            / f"token-{token_id:04d}.json"
        )

        serialized = canonical_json(
            result.art_spec
        )

        digest = (
            "sha256:"
            + hashlib.sha256(
                serialized.encode(
                    "utf-8"
                )
            ).hexdigest()
        )

        if digest != result.art_spec_hash:
            raise RuntimeError(
                "Serialized Art Spec bytes "
                "do not match artSpecHash for "
                f"token #{token_id:04d}."
            )

        if (
            result.art_spec_hash
            in art_spec_hashes
        ):
            raise RuntimeError(
                "Duplicate Art Spec hash detected."
            )

        art_spec_hashes.add(
            result.art_spec_hash
        )

        _atomic_write(
            path,
            serialized,
        )

    manifest = build_manifest(
        results
    )

    _atomic_write(
        output_dir
        / "manifest.json",
        canonical_json(
            manifest
        ),
    )

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate OriginX PHASE 2E "
            "Art Specs #0001–#0010."
        )
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    manifest = write_first_10(
        args.output
    )

    print(
        "Generated:",
        manifest["count"],
        "Art Specs",
    )

    for entry in manifest[
        "entries"
    ]:
        print(
            entry["serial"],
            entry["canonicalName"],
            entry["artSpecHash"],
        )


if __name__ == "__main__":
    main()
