"""OX-GAD PHASE 2D — deterministic Art Spec assembler tests."""

from __future__ import annotations

import copy
import unittest

from oxgad import ART_SPEC_VERSION
from oxgad.structure.assembler import (
    STRUCTURE_ASSEMBLER_VERSION,
    assemble_art_spec,
)
from oxgad.structure.canonical import (
    art_spec_hash,
    canonical_json,
)
from oxgad.structure.input import (
    StructureInput,
)
from oxgad.structure.validator import (
    is_valid_art_spec,
    validate_art_spec,
)


def package(
    *,
    token_id: int = 1,
    serial: str = "#0001",
    name: str = "Vaerkaion",
    tier: str = "RARE",
    generation_theme: str = "Primitive Origin",
    dna_hash_char: str = "a",
    seed: int | None = None,
) -> dict:
    value = {
        "tokenId": token_id,
        "serial": serial,
        "canonicalName": name,
        "tier": tier,
        "generationTheme": generation_theme,
        "dna": {
            "archetype": "ancient-dragon",
            "body": {
                "mass": "heavy",
                "posture": "grounded",
            },
            "lineage": {
                "generation": 1,
            },
        },
        "dnaHash": (
            "sha256:"
            + (
                dna_hash_char
                * 64
            )
        ),
        "resonance": {
            "spectrum": "ember",
            "energyTopology": "radial",
            "intensity": 0.42,
        },
    }

    if seed is not None:
        value["seed"] = seed

    return value


class ArtSpecAssemblerContractTests(
    unittest.TestCase
):
    def test_assembler_version_is_explicit(self):
        self.assertEqual(
            STRUCTURE_ASSEMBLER_VERSION,
            "OX-STRUCTURE-ASSEMBLER-1",
        )

    def test_rare_input_produces_valid_art_spec(self):
        identity = (
            StructureInput.from_mapping(
                package()
            )
        )

        result = assemble_art_spec(
            identity
        )

        self.assertTrue(
            is_valid_art_spec(
                result.art_spec
            )
        )

        validate_art_spec(
            result.art_spec
        )

        self.assertEqual(
            result.art_spec[
                "specVersion"
            ],
            ART_SPEC_VERSION,
        )

    def test_art_spec_hash_matches_canonical_hash(self):
        identity = (
            StructureInput.from_mapping(
                package()
            )
        )

        result = assemble_art_spec(
            identity
        )

        self.assertEqual(
            result.art_spec_hash,
            art_spec_hash(
                result.art_spec
            ),
        )

        self.assertTrue(
            result.art_spec_hash.startswith(
                "sha256:"
            )
        )

    def test_art_rule_hash_is_recorded_outside_spec(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        self.assertTrue(
            result.art_rule_hash.startswith(
                "sha256:"
            )
        )

        self.assertNotIn(
            "artRuleHash",
            result.art_spec,
        )


class IdentityPreservationTests(
    unittest.TestCase
):
    def test_identity_is_preserved(self):
        source = package()

        identity = (
            StructureInput.from_mapping(
                source
            )
        )

        result = assemble_art_spec(
            identity
        )

        art_identity = (
            result.art_spec[
                "identity"
            ]
        )

        self.assertEqual(
            art_identity["tokenId"],
            source["tokenId"],
        )

        self.assertEqual(
            art_identity["serial"],
            source["serial"],
        )

        self.assertEqual(
            art_identity[
                "canonicalName"
            ],
            source[
                "canonicalName"
            ],
        )

        self.assertEqual(
            art_identity["tier"],
            source["tier"],
        )

        self.assertEqual(
            art_identity["dna"],
            source["dna"],
        )

        self.assertEqual(
            art_identity["dnaHash"],
            source["dnaHash"],
        )

    def test_input_object_is_not_mutated(self):
        source = package()
        original = copy.deepcopy(
            source
        )

        identity = (
            StructureInput.from_mapping(
                source
            )
        )

        assemble_art_spec(
            identity
        )

        self.assertEqual(
            source,
            original,
        )

    def test_rare_maps_to_primitive(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package(
                    tier="RARE",
                    generation_theme=(
                        "Primitive Origin"
                    ),
                )
            )
        )

        self.assertEqual(
            result.art_spec[
                "identity"
            ][
                "era"
            ],
            "Primitive Origin",
        )

    def test_epic_maps_to_evolved(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package(
                    token_id=1001,
                    serial="#1001",
                    tier="EPIC",
                    generation_theme=(
                        "Evolved Origin"
                    ),
                    dna_hash_char="b",
                )
            )
        )

        self.assertEqual(
            result.art_spec[
                "identity"
            ][
                "era"
            ],
            "Evolved Origin",
        )

        self.assertTrue(
            is_valid_art_spec(
                result.art_spec
            )
        )

    def test_legendary_maps_to_ascended(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package(
                    token_id=3001,
                    serial="#3001",
                    tier="LEGENDARY",
                    generation_theme=(
                        "Ascended Origin"
                    ),
                    dna_hash_char="c",
                )
            )
        )

        self.assertEqual(
            result.art_spec[
                "identity"
            ][
                "era"
            ],
            "Ascended Origin",
        )

        self.assertTrue(
            is_valid_art_spec(
                result.art_spec
            )
        )


class DeterminismTests(
    unittest.TestCase
):
    def test_same_input_produces_identical_spec(self):
        first = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        second = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        self.assertEqual(
            first.seed,
            second.seed,
        )

        self.assertEqual(
            first.art_spec,
            second.art_spec,
        )

        self.assertEqual(
            first.art_spec_hash,
            second.art_spec_hash,
        )

        self.assertEqual(
            first.art_rule_hash,
            second.art_rule_hash,
        )

        self.assertEqual(
            canonical_json(
                first.art_spec
            ),
            canonical_json(
                second.art_spec
            ),
        )

    def test_explicit_seed_is_preserved(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package(
                    seed=987654321,
                )
            )
        )

        self.assertEqual(
            result.seed,
            987654321,
        )

        self.assertEqual(
            result.art_spec["seed"],
            987654321,
        )

    def test_identity_change_changes_art_spec_hash(self):
        first = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        second = assemble_art_spec(
            StructureInput.from_mapping(
                package(
                    token_id=2,
                    serial="#0002",
                    name="Kaeloryx",
                    dna_hash_char="b",
                )
            )
        )

        self.assertNotEqual(
            first.art_spec_hash,
            second.art_spec_hash,
        )


class GovernanceTests(
    unittest.TestCase
):
    def test_resonance_remains_narrative_only(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        resonance = result.art_spec[
            "resonance"
        ]

        self.assertIs(
            resonance[
                "narrativeOnly"
            ],
            True,
        )

    def test_manual_approval_remains_required(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        quality = result.art_spec[
            "qualityRequirements"
        ]

        self.assertIs(
            quality[
                "requireManualApproval"
            ],
            True,
        )

        self.assertEqual(
            quality[
                "canonicalApprovalMode"
            ],
            "MANUAL_REQUIRED",
        )

    def test_microdetail_cannot_mask_bad_anatomy(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        constraints = result.art_spec[
            "negativeConstraints"
        ]

        self.assertIs(
            constraints[
                "allowDetailToMaskBadAnatomy"
            ],
            False,
        )


class StructuralMeaningTests(
    unittest.TestCase
):
    def test_material_library_is_populated(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        materials = result.art_spec[
            "materials"
        ]

        self.assertGreaterEqual(
            len(
                materials[
                    "libraryRefs"
                ]
            ),
            3,
        )

        self.assertIn(
            "dragonPrimary",
            materials[
                "assignments"
            ],
        )

    def test_environment_has_real_depth_layers(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        layers = result.art_spec[
            "environment"
        ][
            "depthLayers"
        ]

        self.assertTrue(
            layers["foreground"]
        )

        self.assertTrue(
            layers["midground"]
        )

        self.assertTrue(
            layers["background"]
        )

    def test_camera_targets_canonical_identity(self):
        result = assemble_art_spec(
            StructureInput.from_mapping(
                package()
            )
        )

        self.assertEqual(
            result.art_spec[
                "camera"
            ][
                "focalTarget"
            ],
            "Vaerkaion",
        )


if __name__ == "__main__":
    unittest.main()
