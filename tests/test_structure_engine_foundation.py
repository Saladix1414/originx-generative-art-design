"""OX-GAD PHASE 2B — Structure Engine foundation tests."""

from __future__ import annotations

import unittest

from oxgad.structure.deterministic import (
    STRUCTURE_DETERMINISM_VERSION,
    DeterministicSelectionError,
    derive_seed,
    deterministic_choice,
    deterministic_index,
    resolve_seed,
)
from oxgad.structure.input import (
    StructureInput,
    StructureInputError,
)
from oxgad.structure.rules import (
    STRUCTURE_RULESET_VERSION,
    StructureRuleError,
    era_for_tier,
)


DNA_HASH_A = (
    "sha256:"
    + ("a" * 64)
)

DNA_HASH_B = (
    "sha256:"
    + ("b" * 64)
)


def fixture(
    *,
    dna_hash: str = DNA_HASH_A,
    seed: int | None = None,
) -> dict:
    value = {
        "tokenId": 1,
        "serial": "#0001",
        "canonicalName": "Vaerkaion",
        "tier": "RARE",
        "generationTheme": "Primitive Origin",
        "dna": {
            "archetype": "ancient-dragon",
            "body": {
                "mass": "heavy",
            },
        },
        "dnaHash": dna_hash,
        "resonance": {
            "spectrum": "ember",
            "intensity": 0.42,
        },
    }

    if seed is not None:
        value["seed"] = seed

    return value


class StructureInputTests(
    unittest.TestCase
):
    def test_valid_public_identity_package_is_accepted(self):
        value = StructureInput.from_mapping(
            fixture()
        )

        self.assertEqual(
            value.token_id,
            1,
        )

        self.assertEqual(
            value.serial,
            "#0001",
        )

        self.assertEqual(
            value.tier,
            "RARE",
        )

    def test_unknown_fields_are_rejected(self):
        value = fixture()
        value["buyerEmail"] = (
            "private@example.invalid"
        )

        with self.assertRaises(
            StructureInputError
        ):
            StructureInput.from_mapping(
                value
            )

    def test_missing_dna_hash_is_rejected(self):
        value = fixture()
        del value["dnaHash"]

        with self.assertRaises(
            StructureInputError
        ):
            StructureInput.from_mapping(
                value
            )

    def test_invalid_hash_format_is_rejected(self):
        value = fixture(
            dna_hash="not-a-hash"
        )

        with self.assertRaises(
            StructureInputError
        ):
            StructureInput.from_mapping(
                value
            )

    def test_empty_dna_is_rejected(self):
        value = fixture()
        value["dna"] = {}

        with self.assertRaises(
            StructureInputError
        ):
            StructureInput.from_mapping(
                value
            )

    def test_boolean_token_id_is_rejected(self):
        value = fixture()
        value["tokenId"] = True

        with self.assertRaises(
            StructureInputError
        ):
            StructureInput.from_mapping(
                value
            )


class DeterminismTests(
    unittest.TestCase
):
    def test_determinism_version_is_explicit(self):
        self.assertEqual(
            STRUCTURE_DETERMINISM_VERSION,
            "OX-STRUCTURE-DETERMINISM-1",
        )

    def test_same_input_derives_same_seed(self):
        first = StructureInput.from_mapping(
            fixture()
        )

        second = StructureInput.from_mapping(
            fixture()
        )

        self.assertEqual(
            derive_seed(first),
            derive_seed(second),
        )

    def test_identity_change_changes_seed(self):
        first = StructureInput.from_mapping(
            fixture(
                dna_hash=DNA_HASH_A
            )
        )

        second = StructureInput.from_mapping(
            fixture(
                dna_hash=DNA_HASH_B
            )
        )

        self.assertNotEqual(
            derive_seed(first),
            derive_seed(second),
        )

    def test_explicit_seed_is_preserved(self):
        value = StructureInput.from_mapping(
            fixture(
                seed=987654321
            )
        )

        self.assertEqual(
            resolve_seed(value),
            987654321,
        )

    def test_deterministic_index_is_stable(self):
        first = deterministic_index(
            seed=42,
            namespace="dragon.head",
            size=11,
        )

        second = deterministic_index(
            seed=42,
            namespace="dragon.head",
            size=11,
        )

        self.assertEqual(
            first,
            second,
        )

    def test_deterministic_choice_is_stable(self):
        options = (
            "obsidian",
            "basalt",
            "oxidized-steel",
        )

        first = deterministic_choice(
            options,
            seed=42,
            namespace="materials.primary",
        )

        second = deterministic_choice(
            options,
            seed=42,
            namespace="materials.primary",
        )

        self.assertEqual(
            first,
            second,
        )

    def test_empty_choice_is_rejected(self):
        with self.assertRaises(
            DeterministicSelectionError
        ):
            deterministic_choice(
                (),
                seed=42,
                namespace="invalid",
            )


class TierRuleTests(
    unittest.TestCase
):
    def test_ruleset_version_is_explicit(self):
        self.assertEqual(
            STRUCTURE_RULESET_VERSION,
            "OX-STRUCTURE-RULES-1",
        )

    def test_rare_maps_to_primitive_origin(self):
        self.assertEqual(
            era_for_tier("RARE"),
            "Primitive Origin",
        )

    def test_epic_maps_to_evolved_origin(self):
        self.assertEqual(
            era_for_tier("EPIC"),
            "Evolved Origin",
        )

    def test_legendary_maps_to_ascended_origin(self):
        self.assertEqual(
            era_for_tier("LEGENDARY"),
            "Ascended Origin",
        )

    def test_unknown_tier_fails_closed(self):
        with self.assertRaises(
            StructureRuleError
        ):
            era_for_tier(
                "MYTHIC"
            )


if __name__ == "__main__":
    unittest.main()
