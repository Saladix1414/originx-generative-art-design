"""OX-GAD PHASE 2F — Structure Engine closure tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from oxgad.structure import api
from oxgad.structure.canonical import canonical_sha256
from oxgad.structure.validator import is_valid_art_spec


ROOT = Path(__file__).resolve().parents[1]

CLOSURE = (
    ROOT
    / "docs"
    / "architecture"
    / "phase2-closure.json"
)

FIRST10 = (
    ROOT
    / "docs"
    / "architecture"
    / "phase2e-first-10-manifest.json"
)


def package() -> dict:
    dna = {
        "archetype": "ancient-dragon",
        "body": {
            "mass": "heavy",
            "posture": "grounded",
        },
    }

    return {
        "tokenId": 1,
        "serial": "#0001",
        "canonicalName": "Vaerkaion",
        "tier": "RARE",
        "generationTheme": "Primitive Origin",
        "dna": dna,
        "dnaHash": canonical_sha256(dna),
        "resonance": {
            "spectrum": "ember",
            "narrativeRole": "visual influence only",
        },
    }


class StructurePublicApiTests(unittest.TestCase):
    def test_public_contract_is_explicit(self):
        expected = {
            "STRUCTURE_ASSEMBLER_VERSION",
            "STRUCTURE_DETERMINISM_VERSION",
            "STRUCTURE_RULESET_VERSION",
            "ArtSpecAssembly",
            "ArtSpecAssemblyError",
            "DeterministicSelectionError",
            "StructureInput",
            "StructureInputError",
            "StructureRuleError",
            "assemble_art_spec",
            "derive_seed",
            "deterministic_choice",
            "deterministic_index",
            "era_for_tier",
            "resolve_seed",
            "tier_rule",
        }

        self.assertEqual(
            set(api.__all__),
            expected,
        )

    def test_versions_are_stable(self):
        self.assertEqual(
            api.STRUCTURE_ASSEMBLER_VERSION,
            "OX-STRUCTURE-ASSEMBLER-1",
        )
        self.assertEqual(
            api.STRUCTURE_DETERMINISM_VERSION,
            "OX-STRUCTURE-DETERMINISM-1",
        )
        self.assertEqual(
            api.STRUCTURE_RULESET_VERSION,
            "OX-STRUCTURE-RULES-1",
        )

    def test_public_api_builds_valid_spec(self):
        first = api.assemble_art_spec(
            api.StructureInput.from_mapping(
                package()
            )
        )

        second = api.assemble_art_spec(
            api.StructureInput.from_mapping(
                package()
            )
        )

        self.assertTrue(
            is_valid_art_spec(
                first.art_spec
            )
        )

        self.assertEqual(
            first.art_spec_hash,
            second.art_spec_hash,
        )

        self.assertEqual(
            first.art_spec["identity"]["dna"],
            package()["dna"],
        )


class StructureClosureEvidenceTests(unittest.TestCase):
    def test_closure_is_complete(self):
        closure = json.loads(
            CLOSURE.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            closure["closureVersion"],
            "OX-STRUCTURE-CLOSURE-1",
        )
        self.assertEqual(
            closure["phase"],
            2,
        )
        self.assertEqual(
            closure["status"],
            "COMPLETE",
        )

    def test_first10_manifest_hash_matches(self):
        closure = json.loads(
            CLOSURE.read_text(
                encoding="utf-8"
            )
        )

        first10 = json.loads(
            FIRST10.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            closure["first10ManifestHash"],
            canonical_sha256(first10),
        )

    def test_first10_art_hashes_are_unique(self):
        closure = json.loads(
            CLOSURE.read_text(
                encoding="utf-8"
            )
        )

        hashes = closure[
            "first10ArtSpecHashes"
        ]

        self.assertEqual(
            len(hashes),
            10,
        )
        self.assertEqual(
            len(set(hashes)),
            10,
        )

    def test_first10_dna_hashes_are_unique(self):
        closure = json.loads(
            CLOSURE.read_text(
                encoding="utf-8"
            )
        )

        hashes = closure[
            "first10DnaHashes"
        ]

        self.assertEqual(
            len(hashes),
            10,
        )
        self.assertEqual(
            len(set(hashes)),
            10,
        )

    def test_render_runtime_remains_out_of_scope(self):
        closure = json.loads(
            CLOSURE.read_text(
                encoding="utf-8"
            )
        )

        non_goals = set(
            closure["nonGoals"]
        )

        self.assertIn(
            "image-generation",
            non_goals,
        )
        self.assertIn(
            "model-runtime",
            non_goals,
        )
        self.assertIn(
            "prompt-compilation",
            non_goals,
        )


if __name__ == "__main__":
    unittest.main()
