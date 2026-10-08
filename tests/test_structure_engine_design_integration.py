"""PHASE 3D — Grammar-to-Structure integration tests."""

import json
import unittest
from pathlib import Path

from oxgad.design.integration import integrated_design_hash
from oxgad.structure.assembler import assemble_art_spec
from oxgad.structure.first10 import (
    build_manifest,
    first_10_packages,
    generate_first_10,
)
from oxgad.structure.input import StructureInput


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = (
    ROOT
    / "docs"
    / "architecture"
    / "phase2e-first-10-manifest.json"
)


class GrammarToStructureTests(unittest.TestCase):
    def test_assembly_exposes_design_hash(self):
        identity = StructureInput.from_mapping(
            first_10_packages()[0]
        )
        result = assemble_art_spec(identity)

        self.assertTrue(
            result.design_hash.startswith("sha256:")
        )

    def test_design_hash_matches_integrated_contract(self):
        identity = StructureInput.from_mapping(
            first_10_packages()[0]
        )
        result = assemble_art_spec(identity)

        self.assertEqual(
            result.design_hash,
            integrated_design_hash(
                tier=identity.tier,
                seed=result.seed,
            ),
        )

    def test_design_hash_remains_external_to_art_spec(self):
        identity = StructureInput.from_mapping(
            first_10_packages()[0]
        )
        result = assemble_art_spec(identity)

        self.assertNotIn(
            "designHash",
            result.art_spec,
        )
        self.assertNotIn(
            "artRuleHash",
            result.art_spec,
        )

    def test_repeated_assembly_preserves_design_hash(self):
        identity = StructureInput.from_mapping(
            first_10_packages()[0]
        )

        first = assemble_art_spec(identity)
        second = assemble_art_spec(identity)

        self.assertEqual(
            first.design_hash,
            second.design_hash,
        )
        self.assertEqual(
            first.art_spec_hash,
            second.art_spec_hash,
        )

    def test_first10_design_hashes_are_unique(self):
        results = generate_first_10()

        hashes = {
            result.design_hash
            for result in results
        }

        self.assertEqual(len(hashes), 10)

    def test_phase2_art_spec_hashes_are_preserved(self):
        historical = json.loads(
            HISTORICAL.read_text(encoding="utf-8")
        )

        expected = [
            item["artSpecHash"]
            for item in historical["entries"]
        ]

        current = [
            result.art_spec_hash
            for result in generate_first_10()
        ]

        self.assertEqual(current, expected)

    def test_phase2_manifest_is_byte_meaning_preserved(self):
        historical = json.loads(
            HISTORICAL.read_text(encoding="utf-8")
        )

        current = build_manifest(
            generate_first_10()
        )

        self.assertEqual(current, historical)


if __name__ == "__main__":
    unittest.main()
