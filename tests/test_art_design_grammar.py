"""Tests for OX-ART-GRAMMAR-1."""

import unittest

from oxgad.design.grammar import (
    ART_DESIGN_GRAMMAR_VERSION,
    DETAIL_AUTHORITY,
    DOMAIN_ORDER,
    ArtDesignGrammarError,
    compile_art_design_grammar,
    validate_art_design_grammar,
)


class ArtDesignGrammarContractTests(unittest.TestCase):
    def test_version_is_explicit(self):
        self.assertEqual(
            ART_DESIGN_GRAMMAR_VERSION,
            "OX-ART-GRAMMAR-1",
        )

    def test_detail_authority_is_macro_first(self):
        self.assertEqual(
            DETAIL_AUTHORITY,
            ("MACRO", "MESO", "MICRO"),
        )

    def test_domain_order_is_explicit(self):
        self.assertEqual(
            DOMAIN_ORDER,
            (
                "morphology",
                "anatomy",
                "materials",
                "technology",
                "augmentation",
                "architecture",
                "lighting",
                "atmosphere",
                "weathering",
                "ornament",
                "damage",
            ),
        )

    def test_all_tiers_compile(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            grammar = compile_art_design_grammar(tier)
            validate_art_design_grammar(grammar)

    def test_unknown_tier_fails_closed(self):
        with self.assertRaises(ArtDesignGrammarError):
            compile_art_design_grammar("MYTHIC")


class TierEvolutionGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rare = compile_art_design_grammar("RARE")
        cls.epic = compile_art_design_grammar("EPIC")
        cls.legendary = compile_art_design_grammar("LEGENDARY")

    def values(self, domain):
        return [
            grammar["domains"][domain]["intensity"]
            for grammar in (
                self.rare,
                self.epic,
                self.legendary,
            )
        ]

    def test_canonical_era_mapping(self):
        self.assertEqual(
            self.rare["era"],
            "Primitive Origin",
        )
        self.assertEqual(
            self.epic["era"],
            "Evolved Origin",
        )
        self.assertEqual(
            self.legendary["era"],
            "Ascended Origin",
        )

    def test_evolution_rank_is_monotonic(self):
        self.assertEqual(
            [
                self.rare["evolutionRank"],
                self.epic["evolutionRank"],
                self.legendary["evolutionRank"],
            ],
            [1, 2, 3],
        )

    def test_morphology_evolves_monotonically(self):
        self.assertEqual(
            self.values("morphology"),
            [1, 2, 3],
        )

    def test_technology_evolves_monotonically(self):
        self.assertEqual(
            self.values("technology"),
            [1, 2, 3],
        )

    def test_augmentation_evolves_monotonically(self):
        self.assertEqual(
            self.values("augmentation"),
            [1, 2, 3],
        )

    def test_weathering_decreases_with_refinement(self):
        self.assertEqual(
            self.values("weathering"),
            [3, 2, 1],
        )

    def test_damage_decreases_with_refinement(self):
        self.assertEqual(
            self.values("damage"),
            [3, 2, 1],
        )

    def test_ornament_does_not_scale_to_excess(self):
        self.assertEqual(
            self.values("ornament"),
            [1, 2, 2],
        )

    def test_legendary_is_not_just_more_weathered(self):
        self.assertLess(
            self.legendary["domains"]["weathering"]["intensity"],
            self.rare["domains"]["weathering"]["intensity"],
        )


class GrammarInvariantTests(unittest.TestCase):
    def test_anatomy_before_detail_is_mandatory(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            grammar = compile_art_design_grammar(tier)
            self.assertTrue(
                grammar["invariants"]["anatomyBeforeDetail"]
            )

    def test_structural_evolution_not_brightness(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            grammar = compile_art_design_grammar(tier)
            self.assertTrue(
                grammar["invariants"][
                    "structuralEvolutionNotBrightness"
                ]
            )

    def test_random_ornament_is_forbidden(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            grammar = compile_art_design_grammar(tier)
            self.assertTrue(
                grammar["invariants"][
                    "randomOrnamentForbidden"
                ]
            )

    def test_provider_independence_is_explicit(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            grammar = compile_art_design_grammar(tier)
            self.assertTrue(
                grammar["invariants"]["providerIndependent"]
            )

    def test_compilation_returns_isolated_objects(self):
        first = compile_art_design_grammar("RARE")
        second = compile_art_design_grammar("RARE")

        first["domains"]["damage"]["intensity"] = 1

        self.assertEqual(
            second["domains"]["damage"]["intensity"],
            3,
        )

    def test_invalid_domain_intensity_is_rejected(self):
        grammar = compile_art_design_grammar("RARE")
        grammar["domains"]["damage"]["intensity"] = 99

        with self.assertRaises(ArtDesignGrammarError):
            validate_art_design_grammar(grammar)

    def test_invalid_detail_authority_is_rejected(self):
        grammar = compile_art_design_grammar("RARE")
        grammar["invariants"]["detailAuthority"] = [
            "MICRO",
            "MESO",
            "MACRO",
        ]

        with self.assertRaises(ArtDesignGrammarError):
            validate_art_design_grammar(grammar)


class ArtRuleCompatibilityTests(unittest.TestCase):
    def test_catalog_snapshot_is_populated(self):
        grammar = compile_art_design_grammar("RARE")
        catalog = grammar["catalog"]

        self.assertTrue(catalog["bodyMass"])
        self.assertTrue(catalog["silhouette"])
        self.assertTrue(catalog["armor"])
        self.assertTrue(catalog["technology"])
        self.assertTrue(catalog["architecture"])
        self.assertTrue(catalog["materials"]["primary"])
        self.assertTrue(catalog["lighting"])

    def test_tiers_do_not_share_identical_grammar(self):
        rare = compile_art_design_grammar("RARE")
        epic = compile_art_design_grammar("EPIC")
        legendary = compile_art_design_grammar("LEGENDARY")

        self.assertNotEqual(
            rare["domains"],
            epic["domains"],
        )
        self.assertNotEqual(
            epic["domains"],
            legendary["domains"],
        )


if __name__ == "__main__":
    unittest.main()
