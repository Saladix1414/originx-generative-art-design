"""OX-GAD PHASE 4E — Render Compiler closure tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from oxgad import (
    ART_SPEC_VERSION,
    RENDER_VERSION,
)
from oxgad.render import (
    RENDER_COMPILER_VERSION,
    RENDER_FIRST10_MANIFEST_VERSION,
    build_first_10_render_manifest,
    compile_render_plan,
    load_render_schema,
)
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

PHASE4_RENDER = (
    ROOT
    / "docs"
    / "architecture"
    / "phase4d-first-10-render-manifest.json"
)

PHASE4_CLOSURE = (
    ROOT
    / "docs"
    / "architecture"
    / "phase4-closure.json"
)


class Phase4ClosureTests(unittest.TestCase):
    def closure(self):
        return json.loads(
            PHASE4_CLOSURE.read_text(encoding="utf-8")
        )

    def test_phase_is_complete(self):
        value = self.closure()

        self.assertEqual(value["phase"], 4)
        self.assertEqual(value["status"], "COMPLETE")
        self.assertEqual(
            value["closureVersion"],
            "OX-RENDER-CLOSURE-1",
        )

    def test_versions_match_runtime(self):
        value = self.closure()

        self.assertEqual(
            value["artSpecVersion"],
            ART_SPEC_VERSION,
        )
        self.assertEqual(
            value["renderVersion"],
            RENDER_VERSION,
        )
        self.assertEqual(
            value["renderCompilerVersion"],
            RENDER_COMPILER_VERSION,
        )
        self.assertEqual(
            value["first10ManifestVersion"],
            RENDER_FIRST10_MANIFEST_VERSION,
        )

    def test_closure_is_canonical_json(self):
        raw = PHASE4_CLOSURE.read_text(encoding="utf-8")
        value = json.loads(raw)

        self.assertEqual(raw, canonical_json(value))

    def test_render_schema_hash_matches(self):
        value = self.closure()
        schema = load_render_schema()

        self.assertEqual(
            value["renderSchemaHash"],
            canonical_sha256(schema),
        )

    def test_phase2_manifest_hash_matches(self):
        value = self.closure()
        phase2 = json.loads(
            PHASE2.read_text(encoding="utf-8")
        )

        self.assertEqual(
            value["phase2ManifestHash"],
            canonical_sha256(phase2),
        )

    def test_render_manifest_hash_matches(self):
        value = self.closure()
        manifest = json.loads(
            PHASE4_RENDER.read_text(encoding="utf-8")
        )

        self.assertEqual(
            value["phase4RenderManifestHash"],
            canonical_sha256(manifest),
        )

    def test_render_manifest_reproduces_exactly(self):
        stored = json.loads(
            PHASE4_RENDER.read_text(encoding="utf-8")
        )

        self.assertEqual(
            stored,
            build_first_10_render_manifest(),
        )

    def test_first10_render_hashes_match_runtime(self):
        value = self.closure()
        runtime = [
            compile_render_plan(assembly).render_plan_hash
            for assembly in generate_first_10()
        ]

        self.assertEqual(
            value["first10RenderPlanHashes"],
            runtime,
        )
        self.assertEqual(len(runtime), 10)
        self.assertEqual(len(set(runtime)), 10)

    def test_model_binding_remains_unbound(self):
        value = self.closure()

        self.assertEqual(
            value["modelBindingStatus"],
            "UNBOUND",
        )

        for assembly in generate_first_10():
            plan = compile_render_plan(assembly).render_plan
            binding = plan["modelBinding"]

            self.assertEqual(binding["status"], "UNBOUND")
            self.assertIsNone(binding["modelName"])
            self.assertIsNone(binding["modelVersion"])
            self.assertIsNone(binding["modelHash"])

    def test_execution_remains_disabled(self):
        value = self.closure()

        self.assertIs(value["executionAllowed"], False)
        self.assertEqual(
            value["executionPolicy"],
            "LOCAL_FIRST",
        )

        for assembly in generate_first_10():
            policy = compile_render_plan(
                assembly
            ).render_plan["executionPolicy"]

            self.assertIs(
                policy["executionAllowed"],
                False,
            )
            self.assertEqual(
                policy["target"],
                "UNBOUND",
            )

    def test_detail_authority_is_preserved(self):
        self.assertEqual(
            self.closure()["detailAuthority"],
            ["MACRO", "MESO", "MICRO"],
        )

    def test_phase2_history_remains_exact(self):
        stored = json.loads(
            PHASE2.read_text(encoding="utf-8")
        )

        self.assertEqual(
            build_manifest(generate_first_10()),
            stored,
        )

    def test_next_phase_is_hardware_detection(self):
        self.assertEqual(
            self.closure()["nextPhase"],
            "PHASE 5 — Hardware Detection",
        )


if __name__ == "__main__":
    unittest.main()
