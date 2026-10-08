"""OX-GAD PHASE 3E — Art Design Grammar closure tests."""

import json
import unittest
from pathlib import Path

from oxgad.design.art_rules import ART_RULE_CATALOG_VERSION
from oxgad.design.grammar import ART_DESIGN_GRAMMAR_VERSION
from oxgad.design.integration import (
    ART_DESIGN_INTEGRATION_VERSION,
)
from oxgad.structure.assembler import STRUCTURE_ASSEMBLER_VERSION
from oxgad.structure.canonical import (
    canonical_json,
    canonical_sha256,
)
from oxgad.structure.first10 import (
    build_manifest,
    generate_first_10,
)


ROOT = Path(__file__).resolve().parents[1]

PHASE2 = (
    ROOT
    / "docs"
    / "architecture"
    / "phase2e-first-10-manifest.json"
)

PHASE3 = (
    ROOT
    / "docs"
    / "architecture"
    / "phase3-closure.json"
)


class Phase3ClosureTests(unittest.TestCase):
    def closure(self):
        return json.loads(
            PHASE3.read_text(encoding="utf-8")
        )

    def test_phase_is_complete(self):
        closure = self.closure()

        self.assertEqual(closure["phase"], 3)
        self.assertEqual(closure["status"], "COMPLETE")
        self.assertEqual(
            closure["closureVersion"],
            "OX-ART-DESIGN-CLOSURE-1",
        )

    def test_versions_match_runtime(self):
        closure = self.closure()

        self.assertEqual(
            closure["artRuleCatalogVersion"],
            ART_RULE_CATALOG_VERSION,
        )
        self.assertEqual(
            closure["artDesignGrammarVersion"],
            ART_DESIGN_GRAMMAR_VERSION,
        )
        self.assertEqual(
            closure["artDesignIntegrationVersion"],
            ART_DESIGN_INTEGRATION_VERSION,
        )
        self.assertEqual(
            closure["structureAssemblerVersion"],
            STRUCTURE_ASSEMBLER_VERSION,
        )

    def test_closure_is_canonical_json(self):
        raw = PHASE3.read_text(encoding="utf-8")
        value = json.loads(raw)

        self.assertEqual(
            raw,
            canonical_json(value),
        )

    def test_phase2_manifest_hash_matches(self):
        phase2 = json.loads(
            PHASE2.read_text(encoding="utf-8")
        )
        closure = self.closure()

        self.assertEqual(
            closure["phase2ManifestHash"],
            canonical_sha256(phase2),
        )

    def test_historical_art_spec_hashes_are_preserved(self):
        phase2 = json.loads(
            PHASE2.read_text(encoding="utf-8")
        )
        closure = self.closure()

        historical = [
            item["artSpecHash"]
            for item in phase2["entries"]
        ]

        self.assertEqual(
            closure["first10ArtSpecHashes"],
            historical,
        )

    def test_runtime_manifest_still_matches_phase2(self):
        phase2 = json.loads(
            PHASE2.read_text(encoding="utf-8")
        )

        self.assertEqual(
            build_manifest(generate_first_10()),
            phase2,
        )

    def test_design_hashes_are_unique(self):
        hashes = self.closure()["first10DesignHashes"]

        self.assertEqual(len(hashes), 10)
        self.assertEqual(len(set(hashes)), 10)

    def test_art_rule_hashes_are_recorded(self):
        hashes = self.closure()["first10ArtRuleHashes"]

        self.assertEqual(len(hashes), 10)
        self.assertTrue(
            all(value.startswith("sha256:") for value in hashes)
        )

    def test_rendering_remains_out_of_scope(self):
        non_goals = set(self.closure()["nonGoals"])

        self.assertIn("prompt-compilation", non_goals)
        self.assertIn("image-generation", non_goals)
        self.assertIn("model-runtime", non_goals)
        self.assertIn("provider-execution", non_goals)

    def test_next_phase_is_render_compiler(self):
        self.assertEqual(
            self.closure()["nextPhase"],
            "PHASE 4 — OriginX Render Compiler",
        )


if __name__ == "__main__":
    unittest.main()
