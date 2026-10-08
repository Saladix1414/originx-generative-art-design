"""PHASE 4D — first-ten Render Plan evidence tests."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from oxgad.render import (
    RENDER_COMPILER_VERSION,
    RENDER_FIRST10_MANIFEST_VERSION,
    RENDER_VERSION,
    build_first_10_render_manifest,
    generate_first_10_render_plans,
)
from oxgad.structure.canonical import canonical_json
from oxgad.structure.first10 import generate_first_10


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "docs"
    / "architecture"
    / "phase4d-first-10-render-manifest.json"
)


class First10RenderManifestTests(unittest.TestCase):
    def stored(self):
        return json.loads(
            MANIFEST.read_text(encoding="utf-8")
        )

    def test_manifest_version(self):
        value = self.stored()
        self.assertEqual(
            value["manifestVersion"],
            RENDER_FIRST10_MANIFEST_VERSION,
        )

    def test_runtime_versions_match(self):
        value = self.stored()
        self.assertEqual(
            value["renderVersion"],
            RENDER_VERSION,
        )
        self.assertEqual(
            value["renderCompilerVersion"],
            RENDER_COMPILER_VERSION,
        )

    def test_manifest_is_canonical_json(self):
        raw = MANIFEST.read_text(encoding="utf-8")
        value = json.loads(raw)
        self.assertEqual(raw, canonical_json(value))

    def test_manifest_reproduces_exactly(self):
        self.assertEqual(
            self.stored(),
            build_first_10_render_manifest(),
        )

    def test_exactly_ten_entries_exist(self):
        value = self.stored()
        self.assertEqual(value["count"], 10)
        self.assertEqual(len(value["entries"]), 10)

    def test_render_hashes_are_unique(self):
        hashes = [
            item["renderPlanHash"]
            for item in self.stored()["entries"]
        ]
        self.assertEqual(len(hashes), 10)
        self.assertEqual(len(set(hashes)), 10)

    def test_source_hashes_are_unique(self):
        entries = self.stored()["entries"]

        for key in (
            "artSpecHash",
            "artRuleHash",
            "designHash",
        ):
            values = [item[key] for item in entries]
            self.assertEqual(len(values), 10)
            self.assertEqual(len(set(values)), 10)

    def test_runtime_compilations_match_manifest(self):
        plans = generate_first_10_render_plans()
        stored = self.stored()["entries"]

        self.assertEqual(len(plans), len(stored))

        for result, entry in zip(
            plans,
            stored,
            strict=True,
        ):
            self.assertEqual(
                result.render_plan_hash,
                entry["renderPlanHash"],
            )

    def test_manifest_identity_matches_art_specs(self):
        assemblies = generate_first_10()
        entries = self.stored()["entries"]

        for assembly, entry in zip(
            assemblies,
            entries,
            strict=True,
        ):
            identity = assembly.art_spec["identity"]

            self.assertEqual(
                entry["tokenId"],
                identity["tokenId"],
            )
            self.assertEqual(
                entry["serial"],
                identity["serial"],
            )
            self.assertEqual(
                entry["canonicalName"],
                identity["canonicalName"],
            )
            self.assertEqual(
                entry["dnaHash"],
                identity["dnaHash"],
            )

    def test_model_binding_remains_unbound(self):
        value = self.stored()
        self.assertEqual(
            value["modelBindingStatus"],
            "UNBOUND",
        )
        self.assertTrue(all(
            item["modelBindingStatus"] == "UNBOUND"
            for item in value["entries"]
        ))

    def test_execution_remains_disabled(self):
        value = self.stored()
        self.assertIs(value["executionAllowed"], False)
        self.assertTrue(all(
            item["executionAllowed"] is False
            for item in value["entries"]
        ))

    def test_tampered_snapshot_differs_from_runtime(self):
        forged = copy.deepcopy(self.stored())
        forged["entries"][0]["renderPlanHash"] = (
            "sha256:" + ("0" * 64)
        )

        self.assertNotEqual(
            forged,
            build_first_10_render_manifest(),
        )


if __name__ == "__main__":
    unittest.main()
