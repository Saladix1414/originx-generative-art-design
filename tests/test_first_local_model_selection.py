import unittest

from oxgad.models import (
    MODEL_ACQUISITION_PLAN_VERSION,
    build_first_local_model_plan,
    model_acquisition_plan_hash,
    validate_model_acquisition_plan,
)


class FirstLocalModelSelectionTests(unittest.TestCase):
    def plan(self):
        return build_first_local_model_plan()

    def test_version(self):
        self.assertEqual(
            MODEL_ACQUISITION_PLAN_VERSION,
            "OX-MODEL-ACQUISITION-PLAN-1",
        )

    def test_model_identity_selection(self):
        plan = self.plan()
        self.assertEqual(plan["model"]["modelId"], "originx.sd15.emaonly")
        self.assertEqual(plan["model"]["family"], "stable-diffusion-1")
        self.assertEqual(plan["model"]["version"], "1.5")

    def test_source_is_revision_pinned(self):
        plan = self.plan()
        self.assertEqual(
            plan["source"]["repository"],
            "stable-diffusion-v1-5/stable-diffusion-v1-5",
        )
        self.assertEqual(
            plan["source"]["revision"],
            "f03de327dd89b501a01da37fc5240cf4fdba85a1",
        )

    def test_artifact_hash_and_size_are_pinned(self):
        artifact = self.plan()["artifact"]
        self.assertEqual(
            artifact["expectedSha256"],
            "sha256:6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa",
        )
        self.assertEqual(artifact["expectedSizeBytes"], 4265146304)

    def test_local_cpp_is_initial_target(self):
        runtime = self.plan()["runtimeIntent"]
        self.assertEqual(runtime["runtimeFamily"], "stable-diffusion.cpp")
        self.assertEqual(runtime["requestedTarget"], "LOCAL_CPP")
        self.assertEqual(runtime["runtimeBindingState"], "UNBOUND")

    def test_acquisition_is_not_yet_authorized(self):
        governance = self.plan()["governance"]
        self.assertFalse(governance["downloadAllowed"])
        self.assertFalse(governance["installationAllowed"])
        self.assertFalse(governance["executionAllowed"])
        self.assertFalse(governance["mediaGenerationAllowed"])
        self.assertFalse(governance["selectionGrantsExecutionAuthority"])

    def test_same_plan_same_hash(self):
        first = self.plan()
        second = self.plan()
        self.assertEqual(first, second)
        self.assertEqual(
            model_acquisition_plan_hash(first),
            model_acquisition_plan_hash(second),
        )

    def test_plan_validates(self):
        validate_model_acquisition_plan(self.plan())


if __name__ == "__main__":
    unittest.main()
