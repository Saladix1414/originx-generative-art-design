import unittest
from copy import deepcopy

from oxgad.forge import (
    LOCAL_FORGE_BACKEND_VERSION,
    LocalForgeBackendCompatibilityError,
    declare_local_forge_backend,
    prepare_local_forge_request,
    assess_local_forge_execution,
    validate_local_forge_backend,
    validate_local_forge_backend_for_request,
)
from oxgad.hardware import build_hardware_profile
from tests.test_hardware_detector import observation


HASH = "sha256:" + ("8" * 64)


class LocalForgeBackendInterfaceTests(
    unittest.TestCase
):
    def profile(self):
        return build_hardware_profile(
            observation()
        )

    def request(self, target):
        return prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target=target,
        )

    def backend(self, target):
        backend_id = (
            "originx.local.cpp"
            if target == "LOCAL_CPP"
            else "originx.local.gpu"
        )

        return declare_local_forge_backend(
            backend_id=backend_id,
            target=target,
        )

    def test_backend_version(self):
        self.assertEqual(
            LOCAL_FORGE_BACKEND_VERSION,
            "OX-LOCAL-FORGE-BACKEND-1",
        )

    def test_cpp_descriptor_validates(self):
        value = self.backend("LOCAL_CPP")
        validate_local_forge_backend(value)

        self.assertEqual(
            value["runtime"]["kind"],
            "CPP_NATIVE",
        )

    def test_gpu_descriptor_validates(self):
        value = self.backend("LOCAL_GPU")
        validate_local_forge_backend(value)

        self.assertEqual(
            value["runtime"]["kind"],
            "GPU_NATIVE",
        )

    def test_backend_is_declared_only(self):
        value = self.backend("LOCAL_CPP")

        self.assertEqual(
            value["interfaceMode"],
            "DECLARED_ONLY",
        )
        self.assertFalse(
            value["capabilities"][
                "modelExecutionImplemented"
            ]
        )
        self.assertFalse(
            value["capabilities"][
                "mediaGenerationImplemented"
            ]
        )

    def test_direct_invocation_forbidden(self):
        value = self.backend("LOCAL_CPP")

        self.assertTrue(
            value["governance"][
                "requiresExecutionBoundary"
            ]
        )
        self.assertFalse(
            value["governance"][
                "directInvocationAllowed"
            ]
        )

    def test_cpp_backend_matches_cpp_request(self):
        result = (
            validate_local_forge_backend_for_request(
                self.backend("LOCAL_CPP"),
                self.request("LOCAL_CPP"),
            )
        )

        self.assertTrue(
            result["compatible"]
        )
        self.assertFalse(
            result["executionAuthorityGranted"]
        )
        self.assertFalse(
            result["backendInvocationAllowed"]
        )

    def test_gpu_backend_matches_gpu_request(self):
        result = (
            validate_local_forge_backend_for_request(
                self.backend("LOCAL_GPU"),
                self.request("LOCAL_GPU"),
            )
        )

        self.assertTrue(
            result["compatible"]
        )
        self.assertFalse(
            result["backendInvocationAllowed"]
        )

    def test_target_mismatch_is_rejected(self):
        with self.assertRaises(
            LocalForgeBackendCompatibilityError
        ):
            validate_local_forge_backend_for_request(
                self.backend("LOCAL_CPP"),
                self.request("LOCAL_GPU"),
            )

    def test_compatibility_does_not_mutate_inputs(self):
        backend = self.backend("LOCAL_CPP")
        request = self.request("LOCAL_CPP")

        before_backend = deepcopy(backend)
        before_request = deepcopy(request)

        validate_local_forge_backend_for_request(
            backend,
            request,
        )

        self.assertEqual(
            backend,
            before_backend,
        )
        self.assertEqual(
            request,
            before_request,
        )

    def test_declared_backend_does_not_authorize(self):
        request = self.request("LOCAL_CPP")

        compatibility = (
            validate_local_forge_backend_for_request(
                self.backend("LOCAL_CPP"),
                request,
            )
        )

        decision = assess_local_forge_execution(
            request
        )

        self.assertTrue(
            compatibility["compatible"]
        )
        self.assertFalse(
            compatibility[
                "executionAuthorityGranted"
            ]
        )
        self.assertEqual(
            decision["decision"],
            "DENY",
        )
        self.assertFalse(
            decision["backendInvocationAllowed"]
        )


if __name__ == "__main__":
    unittest.main()
