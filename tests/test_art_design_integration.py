"""Tests for OX-ART-DESIGN-INTEGRATION-1."""

import unittest
from copy import deepcopy

from oxgad.design.art_rules import (
    ART_RULE_CATALOG_VERSION,
    art_rule_hash,
)
from oxgad.design.grammar import (
    ART_DESIGN_GRAMMAR_VERSION,
)
from oxgad.design.integration import (
    ART_DESIGN_INTEGRATION_VERSION,
    ArtDesignIntegrationError,
    compile_integrated_design,
    integrated_design_hash,
    validate_integrated_design,
)
from oxgad.structure.canonical import canonical_sha256


class IntegrationContractTests(unittest.TestCase):
    def test_version_is_explicit(self):
        self.assertEqual(
            ART_DESIGN_INTEGRATION_VERSION,
            "OX-ART-DESIGN-INTEGRATION-1",
        )

    def test_source_versions_are_preserved(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123456789,
        )

        self.assertEqual(
            design["catalogVersion"],
            ART_RULE_CATALOG_VERSION,
        )
        self.assertEqual(
            design["grammarVersion"],
            ART_DESIGN_GRAMMAR_VERSION,
        )

    def test_all_canonical_tiers_compile(self):
        expected = {
            "RARE": ("Primitive Origin", 1),
            "EPIC": ("Evolved Origin", 2),
            "LEGENDARY": ("Ascended Origin", 3),
        }

        for tier, (era, rank) in expected.items():
            design = compile_integrated_design(
                tier=tier,
                seed=123456789,
            )

            self.assertEqual(design["tier"], tier)
            self.assertEqual(design["era"], era)
            self.assertEqual(
                design["evolutionRank"],
                rank,
            )

    def test_integration_invariants_are_explicit(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        invariants = design["integrationInvariants"]

        self.assertTrue(invariants["tierAgreement"])
        self.assertTrue(invariants["eraAgreement"])
        self.assertTrue(
            invariants["evolutionRankAgreement"]
        )
        self.assertTrue(
            invariants["detailAuthorityAgreement"]
        )
        self.assertTrue(
            invariants["providerIndependent"]
        )
        self.assertTrue(
            invariants["renderIndependent"]
        )


class DeterminismTests(unittest.TestCase):
    def test_same_tier_and_seed_are_identical(self):
        first = compile_integrated_design(
            tier="RARE",
            seed=777,
        )
        second = compile_integrated_design(
            tier="RARE",
            seed=777,
        )

        self.assertEqual(first, second)

    def test_same_input_has_same_design_hash(self):
        first = integrated_design_hash(
            tier="EPIC",
            seed=888,
        )
        second = integrated_design_hash(
            tier="EPIC",
            seed=888,
        )

        self.assertEqual(first, second)

    def test_different_seed_changes_design_hash(self):
        first = integrated_design_hash(
            tier="RARE",
            seed=100,
        )
        second = integrated_design_hash(
            tier="RARE",
            seed=101,
        )

        self.assertNotEqual(first, second)

    def test_tier_change_changes_design_hash(self):
        rare = integrated_design_hash(
            tier="RARE",
            seed=999,
        )
        epic = integrated_design_hash(
            tier="EPIC",
            seed=999,
        )

        self.assertNotEqual(rare, epic)

    def test_contract_hash_matches_payload_hash(self):
        design = compile_integrated_design(
            tier="LEGENDARY",
            seed=42,
        )

        payload = {
            key: value
            for key, value in design.items()
            if key != "designHash"
        }

        self.assertEqual(
            design["designHash"],
            canonical_sha256(payload),
        )


class SourceAgreementTests(unittest.TestCase):
    def test_art_rule_hash_is_preserved(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123456789,
        )

        self.assertEqual(
            design["artRuleHash"],
            art_rule_hash(
                tier="RARE",
                seed=123456789,
            ),
        )

    def test_tier_era_and_rank_agree(self):
        for tier in ("RARE", "EPIC", "LEGENDARY"):
            design = compile_integrated_design(
                tier=tier,
                seed=123,
            )

            rules = design["artRules"]
            grammar = design["grammar"]

            self.assertEqual(
                rules["tier"],
                grammar["tier"],
            )
            self.assertEqual(
                rules["era"],
                grammar["era"],
            )
            self.assertEqual(
                rules["evolutionRank"],
                grammar["evolutionRank"],
            )

    def test_detail_authority_agrees(self):
        design = compile_integrated_design(
            tier="EPIC",
            seed=555,
        )

        self.assertEqual(
            design["artRules"]["detailPriority"],
            design["grammar"]["invariants"][
                "detailAuthority"
            ],
        )


class IntegrityTests(unittest.TestCase):
    def test_validation_accepts_canonical_contract(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        validate_integrated_design(design)

    def test_boolean_seed_fails_closed(self):
        with self.assertRaises(ArtDesignIntegrationError):
            compile_integrated_design(
                tier="RARE",
                seed=True,
            )

    def test_negative_seed_fails_closed(self):
        with self.assertRaises(ArtDesignIntegrationError):
            compile_integrated_design(
                tier="RARE",
                seed=-1,
            )

    def test_string_seed_fails_closed(self):
        with self.assertRaises(ArtDesignIntegrationError):
            compile_integrated_design(
                tier="RARE",
                seed="123",
            )

    def test_art_rule_tampering_is_rejected(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        tampered = deepcopy(design)
        tampered["artRules"]["dragon"]["bodyMass"] = (
            "forged-body-mass"
        )

        with self.assertRaises(ArtDesignIntegrationError):
            validate_integrated_design(tampered)

    def test_grammar_tampering_is_rejected(self):
        design = compile_integrated_design(
            tier="EPIC",
            seed=123,
        )

        tampered = deepcopy(design)
        tampered["grammar"]["domains"]["technology"][
            "intensity"
        ] = 3

        with self.assertRaises(ArtDesignIntegrationError):
            validate_integrated_design(tampered)

    def test_art_rule_hash_tampering_is_rejected(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        tampered = deepcopy(design)
        tampered["artRuleHash"] = (
            "sha256:" + ("0" * 64)
        )

        with self.assertRaises(ArtDesignIntegrationError):
            validate_integrated_design(tampered)

    def test_design_hash_tampering_is_rejected(self):
        design = compile_integrated_design(
            tier="LEGENDARY",
            seed=123,
        )

        tampered = deepcopy(design)
        tampered["designHash"] = (
            "sha256:" + ("0" * 64)
        )

        with self.assertRaises(ArtDesignIntegrationError):
            validate_integrated_design(tampered)

    def test_unknown_field_is_rejected(self):
        design = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        tampered = deepcopy(design)
        tampered["provider"] = "forged-provider"

        with self.assertRaises(ArtDesignIntegrationError):
            validate_integrated_design(tampered)

    def test_compilation_returns_isolated_objects(self):
        first = compile_integrated_design(
            tier="RARE",
            seed=123,
        )
        second = compile_integrated_design(
            tier="RARE",
            seed=123,
        )

        first["artRules"]["dragon"]["bodyMass"] = "mutated"

        self.assertNotEqual(
            first["artRules"]["dragon"]["bodyMass"],
            second["artRules"]["dragon"]["bodyMass"],
        )


if __name__ == "__main__":
    unittest.main()
