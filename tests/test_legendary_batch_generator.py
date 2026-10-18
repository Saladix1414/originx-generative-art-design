from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT),
)

from oxgad.structure.legendary_batch_generator import (
    build_spec,
    validate_batch,
)


def main() -> None:
    specs = [
        build_spec(token_id)
        for token_id in range(1, 11)
    ]

    assert len(specs) == 10

    ids = [
        spec["identity"]["tokenId"]
        for spec in specs
    ]

    assert ids == list(
        range(1, 11)
    )

    names = {
        spec["identity"][
            "canonicalName"
        ]
        for spec in specs
    }

    assert len(names) == 10

    dna_hashes = {
        spec["dna"]["dnaHash"]
        for spec in specs
    }

    assert len(dna_hashes) == 10

    powers = {
        spec["powers"][
            "signatureAbility"
        ]
        for spec in specs
    }

    assert len(powers) == 10

    for spec in specs:
        assert (
            spec["identity"]["tier"]
            == "LEGENDARY"
        )

        assert (
            spec["identity"]["cohort"]
            == "GENESIS"
        )

        assert (
            spec["identity"]["era"]
            == "PRIMORDIAL ORIGIN"
        )

        assert (
            spec["qualityTarget"][
                "minimumScore"
            ]
            == 92
        )

        assert (
            spec["resonance"][
                "bindingStatus"
            ]
            ==
            "CANONICAL_BOUND"
        )

        assert (
            spec["glyph"][
                "bindingStatus"
            ]
            ==
            "CANONICAL_BOUND"
        )

        assert (
            spec["akashic"][
                "bindingStatus"
            ]
            ==
            "CANONICAL_BOUND"
        )

        assert (
            spec["akashic"][
                "tokenId"
            ]
            ==
            spec["identity"][
                "tokenId"
            ]
        )

        assert (
            spec["akashic"][
                "appendOnly"
            ]
            is True
        )

        assert (
            spec["akashic"][
                "tamperEvident"
            ]
            is True
        )

        assert (
            isinstance(
                spec["akashic"][
                    "events"
                ],
                list,
            )
        )

        assert (
            spec["akashic"][
                "headHash"
            ].startswith(
                "sha256:"
            )
        )

        assert (
            spec["loreBinding"][
                "bindingStatus"
            ]
            ==
            "CANONICAL_BOUND"
        )

        assert (
            spec["loreBinding"][
                "loreVersion"
            ]
            ==
            "OX-GENESIS-LORE-1"
        )

        assert (
            spec["resonance"][
                "glyphSeed"
            ]
            ==
            spec["glyph"][
                "glyphSeed"
            ]
        )

        assert (
            spec["dna"][
                "bindingStatus"
            ]
            == "CANONICAL_BOUND"
        )

        assert (
            spec["dna"][
                "sourceAuthority"
            ]
            == "OX-GENESIS-IDENTITY-1"
        )

        assert (
            spec["dna"][
                "dnaHash"
            ].startswith("sha256:")
        )

    errors = validate_batch(
        specs
    )

    assert not errors, errors

    # Determinism.
    again = [
        build_spec(token_id)
        for token_id in range(1, 11)
    ]

    assert [
        spec["identityHash"]
        for spec in specs
    ] == [
        spec["identityHash"]
        for spec in again
    ]

    print(
        "TOKEN_RANGE=PASS"
    )

    print(
        "UNIQUE_NAMES=PASS"
    )

    print(
        "CANONICAL_DNA_UNIQUENESS=PASS"
    )

    print(
        "POWER_DIVERSITY=PASS"
    )

    print(
        "INDIVIDUALITY_GATE=PASS"
    )

    print(
        "CANONICAL_LORE_BINDING=BOUND"
    )

    print(
        "DETERMINISM=PASS"
    )

    print(
        "CANONICAL_DNA_BINDING="
        "BOUND"
    )

    print(
        "LEGENDARY_BATCH_GENERATOR=PASS"
    )


if __name__ == "__main__":
    main()
