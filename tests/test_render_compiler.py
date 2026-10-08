"""PHASE 4C — deterministic Render Compiler tests."""

from __future__ import annotations

import copy
import unittest
from dataclasses import replace

from oxgad.render import (
    RENDER_COMPILER_VERSION,
    RenderPlanCompilationError,
    compile_render_plan,
    render_plan_hash,
    validate_render_plan,
)
from oxgad.structure.canonical import canonical_sha256
from oxgad.structure.first10 import generate_first_10


class RenderCompilerTests(unittest.TestCase):
    def assembly(self):
        return generate_first_10()[0]

    def test_compiler_version(self):
        self.assertEqual(
            RENDER_COMPILER_VERSION,
            "OX-RENDER-COMPILER-1",
        )

    def test_compiles_valid_render_plan(self):
        result = compile_render_plan(self.assembly())
        self.assertIs(
            validate_render_plan(result.render_plan),
            result.render_plan,
        )

    def test_render_plan_hash_is_canonical(self):
        result = compile_render_plan(self.assembly())
        self.assertEqual(
            result.render_plan_hash,
            canonical_sha256(result.render_plan),
        )
        self.assertEqual(
            result.render_plan_hash,
            render_plan_hash(result.render_plan),
        )

    def test_source_evidence_is_exact(self):
        assembly = self.assembly()
        result = compile_render_plan(assembly)
        source = result.render_plan["source"]

        self.assertEqual(
            source["artSpecHash"], assembly.art_spec_hash
        )
        self.assertEqual(
            source["artRuleHash"], assembly.art_rule_hash
        )
        self.assertEqual(
            source["designHash"], assembly.design_hash
        )
        self.assertEqual(source["seed"], assembly.seed)

    def test_compilation_is_deterministic(self):
        assembly = self.assembly()
        first = compile_render_plan(assembly)
        second = compile_render_plan(assembly)

        self.assertEqual(first.render_plan, second.render_plan)
        self.assertEqual(
            first.render_plan_hash,
            second.render_plan_hash,
        )

    def test_first10_hashes_are_unique(self):
        hashes = [
            compile_render_plan(value).render_plan_hash
            for value in generate_first_10()
        ]
        self.assertEqual(len(hashes), 10)
        self.assertEqual(len(set(hashes)), 10)

    def test_input_is_not_mutated(self):
        assembly = self.assembly()
        before = copy.deepcopy(assembly.art_spec)
        compile_render_plan(assembly)
        self.assertEqual(assembly.art_spec, before)

    def test_forged_art_spec_hash_is_rejected(self):
        forged = replace(
            self.assembly(),
            art_spec_hash="sha256:" + ("0" * 64),
        )
        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan(forged)

    def test_forged_art_rule_hash_is_rejected(self):
        forged = replace(
            self.assembly(),
            art_rule_hash="sha256:" + ("0" * 64),
        )
        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan(forged)

    def test_forged_design_hash_is_rejected(self):
        forged = replace(
            self.assembly(),
            design_hash="sha256:" + ("0" * 64),
        )
        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan(forged)

    def test_tampered_art_spec_is_rejected(self):
        original = self.assembly()
        art_spec = copy.deepcopy(original.art_spec)
        art_spec["identity"]["canonicalName"] = "Forged"
        forged = replace(original, art_spec=art_spec)

        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan(forged)

    def test_seed_mismatch_is_rejected(self):
        original = self.assembly()
        art_spec = copy.deepcopy(original.art_spec)
        art_spec["seed"] = original.seed + 1
        forged = replace(original, art_spec=art_spec)

        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan(forged)

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(RenderPlanCompilationError):
            compile_render_plan({})

    def test_prompt_program_is_structured(self):
        program = compile_render_plan(
            self.assembly()
        ).render_plan["promptProgram"]

        self.assertEqual(
            program["compilerPolicy"],
            "STRUCTURED_DETERMINISTIC",
        )
        self.assertIs(program["identityPreservation"], True)
        self.assertTrue(
            program["orderedSegments"][0].startswith("identity=")
        )

    def test_model_identity_is_unbound(self):
        binding = compile_render_plan(
            self.assembly()
        ).render_plan["modelBinding"]

        self.assertEqual(binding["status"], "UNBOUND")
        self.assertIsNone(binding["modelName"])
        self.assertIsNone(binding["modelVersion"])
        self.assertIsNone(binding["modelHash"])

    def test_execution_is_disabled(self):
        policy = compile_render_plan(
            self.assembly()
        ).render_plan["executionPolicy"]

        self.assertEqual(policy["policy"], "LOCAL_FIRST")
        self.assertIs(policy["providerIndependent"], True)
        self.assertIs(policy["executionAllowed"], False)
        self.assertEqual(policy["target"], "UNBOUND")

    def test_detail_authority_is_macro_first(self):
        policy = compile_render_plan(
            self.assembly()
        ).render_plan["detailPolicy"]

        self.assertEqual(
            policy["authorityOrder"],
            ["MACRO", "MESO", "MICRO"],
        )
        self.assertIs(policy["macroFirst"], True)
        self.assertIs(
            policy["microCannotMaskBadAnatomy"],
            True,
        )


if __name__ == "__main__":
    unittest.main()
