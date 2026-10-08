"""OX-GAD PHASE 4B — OX-RENDER-1 contract tests."""

from __future__ import annotations

import copy
import unittest

from jsonschema import Draft202012Validator

from oxgad import RENDER_VERSION
from oxgad.render.validator import (
    RenderPlanValidationError,
    is_valid_render_plan,
    load_render_schema,
    validate_render_plan,
)


def valid_render_plan() -> dict:
    return {
        "renderVersion": "OX-RENDER-1",
        "source": {
            "artSpecVersion": "OX-ART-SPEC-1",
            "artSpecHash": "sha256:" + ("1" * 64),
            "artRuleHash": "sha256:" + ("2" * 64),
            "designHash": "sha256:" + ("3" * 64),
            "seed": 42,
        },
        "identity": {
            "tokenId": 1,
            "serial": "#0001",
            "canonicalName": "Vaerkaion",
            "tier": "RARE",
            "era": "Primitive Origin",
            "dnaHash": "sha256:" + ("4" * 64),
        },
        "promptProgram": {
            "compilerPolicy": "STRUCTURED_DETERMINISTIC",
            "identityPreservation": True,
            "orderedSegments": [
                "identity",
                "macro-anatomy",
            ],
        },
        "negativeProgram": {
            "compilerPolicy": "STRUCTURED_DETERMINISTIC",
            "constraints": [
                "no-watermark",
                "no-franchise-imitation",
            ],
        },
        "camera": {
            "projection": "PERSPECTIVE",
            "lensMm": 28,
            "height": "LOW",
            "pitchDegrees": -4.0,
            "yawDegrees": 0.0,
            "rollDegrees": 0.0,
            "focalTarget": "Vaerkaion",
            "distance": "WIDE",
        },
        "composition": {
            "dominance": "low-angle-monumentality",
            "balance": "controlled monumental balance",
            "symmetry": "NEAR_SYMMETRIC",
            "ruleOfThirds": False,
            "environmentRatio": 0.38,
            "depthPriority": "subject-first with monumental depth",
            "leadingGeometry": [
                "cyclopean-stone-complex",
            ],
            "cropPolicy": "FULL_BODY_REQUIRED",
            "subjectOccupancy": 0.72,
            "safeMargin": 0.08,
        },
        "materials": {
            "libraryRefs": [
                "weathered-dark-stone",
            ],
            "assignments": {
                "dragonPrimary": "weathered-dark-stone",
            },
            "weatheringPolicy": (
                "physically coherent controlled weathering"
            ),
        },
        "sampling": {
            "sampler": "UNBOUND",
            "steps": 1,
            "cfg": 0.0,
            "denoise": 1.0,
            "seed": 42,
        },
        "resolution": {
            "width": 64,
            "height": 64,
            "aspectRatio": "1:1",
        },
        "modelBinding": {
            "status": "UNBOUND",
            "modelName": None,
            "modelVersion": None,
            "modelHash": None,
            "requiredCapabilities": [
                "text-conditioned-image-generation",
            ],
        },
        "conditioning": {
            "loraSlots": [],
            "controlNetSlots": [],
        },
        "detailPolicy": {
            "authorityOrder": [
                "MACRO",
                "MESO",
                "MICRO",
            ],
            "macroFirst": True,
            "microCannotMaskBadAnatomy": True,
            "detailDensity": 0.82,
        },
        "upscalePolicy": {
            "mode": "DISABLED",
            "enabled": False,
            "targetResolution": None,
        },
        "executionPolicy": {
            "policy": "LOCAL_FIRST",
            "providerIndependent": True,
            "executionAllowed": False,
            "target": "UNBOUND",
        },
    }


class RenderContractTests(unittest.TestCase):
    def test_render_version(self):
        self.assertEqual(RENDER_VERSION, "OX-RENDER-1")

    def test_schema_is_valid_draft_2020_12(self):
        schema = load_render_schema()
        Draft202012Validator.check_schema(schema)
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_schema_is_closed(self):
        self.assertIs(
            load_render_schema()["additionalProperties"],
            False,
        )

    def test_valid_plan_passes(self):
        plan = valid_render_plan()
        self.assertIs(validate_render_plan(plan), plan)
        self.assertTrue(is_valid_render_plan(plan))

    def test_unknown_field_fails_closed(self):
        plan = valid_render_plan()
        plan["unknownAuthority"] = True
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_invalid_design_hash_is_rejected(self):
        plan = valid_render_plan()
        plan["source"]["designHash"] = "invalid"
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_negative_seed_is_rejected(self):
        plan = valid_render_plan()
        plan["source"]["seed"] = -1
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_seed_above_uint64_is_rejected(self):
        plan = valid_render_plan()
        plan["source"]["seed"] = 18446744073709551616
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_model_name_cannot_be_fabricated(self):
        plan = valid_render_plan()
        plan["modelBinding"]["modelName"] = "fake-model"
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_model_version_cannot_be_fabricated(self):
        plan = valid_render_plan()
        plan["modelBinding"]["modelVersion"] = "1.0"
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_model_hash_cannot_be_fabricated(self):
        plan = valid_render_plan()
        plan["modelBinding"]["modelHash"] = (
            "sha256:" + ("9" * 64)
        )
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_execution_cannot_be_enabled(self):
        plan = valid_render_plan()
        plan["executionPolicy"]["executionAllowed"] = True
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_execution_target_remains_unbound(self):
        plan = valid_render_plan()
        plan["executionPolicy"]["target"] = "LOCAL_GPU"
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_external_first_is_rejected(self):
        plan = valid_render_plan()
        plan["executionPolicy"]["policy"] = "EXTERNAL_FIRST"
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_detail_authority_cannot_be_reversed(self):
        plan = valid_render_plan()
        plan["detailPolicy"]["authorityOrder"] = [
            "MICRO",
            "MESO",
            "MACRO",
        ]
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_identity_preservation_is_mandatory(self):
        plan = valid_render_plan()
        plan["promptProgram"]["identityPreservation"] = False
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_too_small_resolution_is_rejected(self):
        plan = valid_render_plan()
        plan["resolution"]["width"] = 32
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan(plan)

    def test_input_is_not_mutated(self):
        plan = valid_render_plan()
        before = copy.deepcopy(plan)
        validate_render_plan(plan)
        self.assertEqual(plan, before)

    def test_non_object_is_rejected(self):
        with self.assertRaises(RenderPlanValidationError):
            validate_render_plan([])


if __name__ == "__main__":
    unittest.main()
