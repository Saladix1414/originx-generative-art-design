"""OX-GAD PHASE 2C — Art Rule Catalog tests."""

from __future__ import annotations

import unittest

from oxgad.design.art_rules import (
    ART_RULE_CATALOG_VERSION,
    CONTINUITY_MOTIFS,
    DETAIL_PRIORITY,
    FORBIDDEN_VISUAL_MODES,
    UNIVERSE_ANCHORS,
    ArtRuleError,
    art_profile_for_tier,
    art_rule_hash,
    select_art_rules,
)
from oxgad.structure.canonical import (
    canonical_json,
)


class ArtRuleCatalogContractTests(
    unittest.TestCase
):
    def test_catalog_version_is_explicit(self):
        self.assertEqual(
            ART_RULE_CATALOG_VERSION,
            "OX-ART-RULES-1",
        )

    def test_detail_priority_is_macro_first(self):
        self.assertEqual(
            DETAIL_PRIORITY,
            (
                "MACRO",
                "MESO",
                "MICRO",
            ),
        )

    def test_originx_universe_anchors_are_explicit(self):
        required = {
            "dark",
            "monumental",
            "ancient",
            "technological",
            "mysterious",
            "physically-heavy",
            "cinematic",
            "precise",
            "original",
        }

        self.assertTrue(
            required.issubset(
                set(
                    UNIVERSE_ANCHORS
                )
            )
        )

    def test_visual_anti_patterns_are_explicit(self):
        required = {
            "generic-fantasy",
            "generic-cyberpunk",
            "cartoon-styling",
            "excessive-neon",
            "flat-lighting",
            "watermark",
            "uncontrolled-text",
        }

        self.assertTrue(
            required.issubset(
                set(
                    FORBIDDEN_VISUAL_MODES
                )
            )
        )

    def test_cross_tier_continuity_is_explicit(self):
        required = {
            "megalithic-mass",
            "basaltic-foundation",
            "ancient-engineering",
            "monumental-scale",
        }

        self.assertTrue(
            required.issubset(
                set(
                    CONTINUITY_MOTIFS
                )
            )
        )


class TierEvolutionTests(
    unittest.TestCase
):
    def test_rare_profile_is_primitive(self):
        profile = art_profile_for_tier(
            "RARE"
        )

        self.assertEqual(
            profile.era,
            "Primitive Origin",
        )

        self.assertEqual(
            profile.evolution_rank,
            1,
        )

    def test_epic_profile_is_evolved(self):
        profile = art_profile_for_tier(
            "EPIC"
        )

        self.assertEqual(
            profile.era,
            "Evolved Origin",
        )

        self.assertEqual(
            profile.evolution_rank,
            2,
        )

    def test_legendary_profile_is_ascended(self):
        profile = art_profile_for_tier(
            "LEGENDARY"
        )

        self.assertEqual(
            profile.era,
            "Ascended Origin",
        )

        self.assertEqual(
            profile.evolution_rank,
            3,
        )

    def test_progression_is_monotonic(self):
        ranks = [
            art_profile_for_tier(
                tier
            ).evolution_rank
            for tier in (
                "RARE",
                "EPIC",
                "LEGENDARY",
            )
        ]

        self.assertEqual(
            ranks,
            [1, 2, 3],
        )

    def test_unknown_tier_fails_closed(self):
        with self.assertRaises(
            ArtRuleError
        ):
            art_profile_for_tier(
                "MYTHIC"
            )

    def test_tiers_are_not_same_grammar(self):
        rare = art_profile_for_tier(
            "RARE"
        )

        epic = art_profile_for_tier(
            "EPIC"
        )

        legendary = art_profile_for_tier(
            "LEGENDARY"
        )

        self.assertNotEqual(
            rare.architecture_language,
            epic.architecture_language,
        )

        self.assertNotEqual(
            epic.architecture_language,
            legendary.architecture_language,
        )

        self.assertNotEqual(
            rare.augmentation_language,
            legendary.augmentation_language,
        )


class DeterministicArtRuleTests(
    unittest.TestCase
):
    def test_same_tier_and_seed_are_identical(self):
        first = select_art_rules(
            tier="RARE",
            seed=123456789,
        )

        second = select_art_rules(
            tier="RARE",
            seed=123456789,
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            canonical_json(first),
            canonical_json(second),
        )

    def test_art_rule_hash_is_stable(self):
        first = art_rule_hash(
            tier="EPIC",
            seed=42,
        )

        second = art_rule_hash(
            tier="EPIC",
            seed=42,
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertTrue(
            first.startswith(
                "sha256:"
            )
        )

    def test_bundle_carries_rule_version(self):
        result = select_art_rules(
            tier="LEGENDARY",
            seed=99,
        )

        self.assertEqual(
            result["catalogVersion"],
            ART_RULE_CATALOG_VERSION,
        )

    def test_bundle_carries_canonical_era(self):
        self.assertEqual(
            select_art_rules(
                tier="RARE",
                seed=1,
            )["era"],
            "Primitive Origin",
        )

        self.assertEqual(
            select_art_rules(
                tier="EPIC",
                seed=1,
            )["era"],
            "Evolved Origin",
        )

        self.assertEqual(
            select_art_rules(
                tier="LEGENDARY",
                seed=1,
            )["era"],
            "Ascended Origin",
        )

    def test_bundle_preserves_detail_authority_order(self):
        result = select_art_rules(
            tier="RARE",
            seed=17,
        )

        self.assertEqual(
            result[
                "detailPriority"
            ],
            [
                "MACRO",
                "MESO",
                "MICRO",
            ],
        )

        constraints = result[
            "visualConstraints"
        ]

        self.assertIs(
            constraints[
                "macroBeforeMeso"
            ],
            True,
        )

        self.assertIs(
            constraints[
                "mesoBeforeMicro"
            ],
            True,
        )

        self.assertIs(
            constraints[
                "microCannotMaskBadAnatomy"
            ],
            True,
        )

    def test_catalog_output_is_canonicalizable(self):
        value = select_art_rules(
            tier="EPIC",
            seed=123,
        )

        serialized = canonical_json(
            value
        )

        self.assertIn(
            '"catalogVersion":"OX-ART-RULES-1"',
            serialized,
        )


class OriginXEvolutionQualityTests(
    unittest.TestCase
):
    def test_primitive_uses_foundational_material_language(self):
        profile = art_profile_for_tier(
            "RARE"
        )

        self.assertIn(
            "basalt",
            profile.primary_materials,
        )

        self.assertIn(
            "obsidian",
            profile.primary_materials,
        )

    def test_evolved_adds_integrated_technology(self):
        profile = art_profile_for_tier(
            "EPIC"
        )

        combined = " ".join(
            profile.augmentation_language
            + profile.technology_language
        )

        self.assertIn(
            "integrated",
            combined,
        )

    def test_ascended_is_architectonic_not_just_brighter(self):
        profile = art_profile_for_tier(
            "LEGENDARY"
        )

        combined = " ".join(
            profile.silhouette_language
            + profile.architecture_language
            + profile.armor_language
        )

        self.assertIn(
            "architectonic",
            combined,
        )

    def test_all_tiers_preserve_macro_anatomy_priority(self):
        for tier in (
            "RARE",
            "EPIC",
            "LEGENDARY",
        ):
            with self.subTest(
                tier=tier
            ):
                profile = art_profile_for_tier(
                    tier
                )

                self.assertEqual(
                    profile.macro_priorities[0],
                    "anatomy",
                )


if __name__ == "__main__":
    unittest.main()
