import unittest
from copy import deepcopy

from oxgad.forge import (
    assess_local_forge_execution,
    prepare_local_forge_request,
)
from oxgad.hardware import build_hardware_profile
from oxgad.models import (
    MODEL_BINDING_VERSION,
    ModelBindingError,
    apply_model_trust_evidence,
    assess_model_artifact_evidence,
    bind_verified_model_to_local_forge,
    register_model_metadata,
    validate_model_binding,
    validate_model_binding_for_local_forge,
)
from tests.test_hardware_detector import observation


ARTIFACT_A = "sha256:" + ("3" * 64)
ARTIFACT_B = "sha256:" + ("4" * 64)
PLAN_A = "sha256:" + ("5" * 64)
PLAN_B = "sha256:" + ("6" * 64)


class ModelBindingBoundaryTests(unittest.TestCase):
    def verified_model(
        self,
        model_id="originx.bound.model",
        artifact_hash=ARTIFACT_A,
        targets=None,
    ):
        if targets is None:
            targets = ["LOCAL_CPP", "LOCAL_GPU"]

        record = register_model_metadata(
            model_id=model_id,
            name="OriginX Bound Model",
            family="test-family",
            version="1.0",
            supported_targets=targets,
            artifact_sha256=artifact_hash,
            artifact_format="safetensors",
            artifact_size_bytes=4096,
        )

        evidence = assess_model_artifact_evidence(
            record,
            observed_sha256=artifact_hash,
            observed_format="safetensors",
            observed_size_bytes=4096,
        )

        return apply_model_trust_evidence(
            record,
            evidence,
        )

    def request(
        self,
        plan_hash=PLAN_A,
        target="LOCAL_CPP",
    ):
        return prepare_local_forge_request(
            render_plan_hash=plan_hash,
            hardware_profile=build_hardware_profile(observation()),
            requested_target=target,
        )

    def test_version(self):
        self.assertEqual(
            MODEL_BINDING_VERSION,
            "OX-MODEL-BINDING-1",
        )

    def test_verified_binding_validates(self):
        model = self.verified_model()
        request = self.request()
        binding = bind_verified_model_to_local_forge(model, request)
        validate_model_binding(binding)
        validate_model_binding_for_local_forge(binding, model, request)
        self.assertEqual(binding["bindingState"], "VERIFIED_MODEL_BOUND")

    def test_same_inputs_same_binding(self):
        model = self.verified_model()
        request = self.request()
        self.assertEqual(
            bind_verified_model_to_local_forge(model, request),
            bind_verified_model_to_local_forge(model, request),
        )

    def test_binding_hash_tamper_is_rejected(self):
        model = self.verified_model()
        request = self.request()
        binding = bind_verified_model_to_local_forge(model, request)
        binding["bindingHash"] = ARTIFACT_B
        with self.assertRaises(ModelBindingError):
            validate_model_binding(binding)

    def test_cross_model_replay_is_rejected(self):
        model = self.verified_model()
        request = self.request()
        binding = bind_verified_model_to_local_forge(model, request)
        other = self.verified_model(model_id="originx.other.model")
        with self.assertRaises(ModelBindingError):
            validate_model_binding_for_local_forge(binding, other, request)

    def test_cross_artifact_replay_is_rejected(self):
        model = self.verified_model()
        request = self.request()
        binding = bind_verified_model_to_local_forge(model, request)
        other = self.verified_model(artifact_hash=ARTIFACT_B)
        with self.assertRaises(ModelBindingError):
            validate_model_binding_for_local_forge(binding, other, request)

    def test_cross_render_plan_replay_is_rejected(self):
        model = self.verified_model()
        request = self.request(PLAN_A)
        binding = bind_verified_model_to_local_forge(model, request)
        other_request = self.request(PLAN_B)
        with self.assertRaises(ModelBindingError):
            validate_model_binding_for_local_forge(binding, model, other_request)

    def test_cross_target_replay_is_rejected(self):
        model = self.verified_model()
        request = self.request(target="LOCAL_CPP")
        binding = bind_verified_model_to_local_forge(model, request)
        other_request = self.request(target="LOCAL_GPU")
        with self.assertRaises(ModelBindingError):
            validate_model_binding_for_local_forge(binding, model, other_request)

    def test_inputs_are_not_mutated(self):
        model = self.verified_model()
        request = self.request()
        before_model = deepcopy(model)
        before_request = deepcopy(request)
        binding = bind_verified_model_to_local_forge(model, request)
        validate_model_binding_for_local_forge(binding, model, request)
        self.assertEqual(model, before_model)
        self.assertEqual(request, before_request)

    def test_binding_never_authorizes_execution(self):
        model = self.verified_model()
        request = self.request()
        binding = bind_verified_model_to_local_forge(model, request)
        self.assertFalse(binding["governance"]["bindingGrantsExecutionAuthority"])
        self.assertFalse(binding["governance"]["executionAllowed"])
        self.assertFalse(binding["governance"]["backendInvocationAllowed"])
        decision = assess_local_forge_execution(request)
        self.assertEqual(decision["decision"], "DENY")
        self.assertFalse(decision["backendInvocationAllowed"])


if __name__ == "__main__":
    unittest.main()
