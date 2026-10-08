import unittest
from copy import deepcopy

from oxgad.forge import (
    LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION,
    LOCAL_FORGE_EXECUTION_DECISION_VERSION,
    LocalForgeExecutionBlocked,
    assess_local_forge_execution,
    prepare_local_forge_request,
    require_local_forge_execution,
    validate_local_forge_execution_decision,
)
from oxgad.hardware import build_hardware_profile
from tests.test_hardware_detector import observation


HASH = "sha256:" + ("f" * 64)


class LocalForgeExecutionBoundaryTests(
    unittest.TestCase
):
    def profile(self):
        return build_hardware_profile(
            observation()
        )

    def request(self, target="LOCAL_CPP"):
        return prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target=target,
        )

    def test_versions(self):
        self.assertEqual(
            LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION,
            "OX-LOCAL-FORGE-EXECUTION-BOUNDARY-1",
        )
        self.assertEqual(
            LOCAL_FORGE_EXECUTION_DECISION_VERSION,
            "OX-LOCAL-FORGE-EXECUTION-DECISION-1",
        )

    def test_local_cpp_is_denied(self):
        decision = assess_local_forge_execution(
            self.request("LOCAL_CPP")
        )
        validate_local_forge_execution_decision(
            decision
        )
        self.assertEqual(
            decision["decision"],
            "DENY",
        )
        self.assertFalse(
            decision["backendInvocationAllowed"]
        )

    def test_local_gpu_is_denied(self):
        decision = assess_local_forge_execution(
            self.request("LOCAL_GPU")
        )
        self.assertEqual(
            decision["decision"],
            "DENY",
        )
        self.assertFalse(
            decision["backendInvocationAllowed"]
        )

    def test_local_gpu_unknown_reason(self):
        decision = assess_local_forge_execution(
            self.request("LOCAL_GPU")
        )
        self.assertIn(
            "HARDWARE_CAPABILITY_NOT_CONFIRMED",
            decision["reasonCodes"],
        )

    def test_model_unbound_reason(self):
        decision = assess_local_forge_execution(
            self.request()
        )
        self.assertIn(
            "MODEL_UNBOUND",
            decision["reasonCodes"],
        )

    def test_authorization_blocked_reason(self):
        decision = assess_local_forge_execution(
            self.request()
        )
        self.assertIn(
            "AUTHORIZATION_BLOCKED",
            decision["reasonCodes"],
        )

    def test_execution_not_allowed_reason(self):
        decision = assess_local_forge_execution(
            self.request()
        )
        self.assertIn(
            "EXECUTION_NOT_ALLOWED",
            decision["reasonCodes"],
        )

    def test_media_generation_not_allowed(self):
        decision = assess_local_forge_execution(
            self.request()
        )
        self.assertIn(
            "MEDIA_GENERATION_NOT_ALLOWED",
            decision["reasonCodes"],
        )

    def test_canonical_artwork_not_allowed(self):
        decision = assess_local_forge_execution(
            self.request()
        )
        self.assertIn(
            "CANONICAL_ARTWORK_NOT_ALLOWED",
            decision["reasonCodes"],
        )

    def test_require_execution_raises(self):
        with self.assertRaises(
            LocalForgeExecutionBlocked
        ):
            require_local_forge_execution(
                self.request()
            )

    def test_assessment_does_not_mutate_request(self):
        request = self.request()
        before = deepcopy(request)

        assess_local_forge_execution(request)

        self.assertEqual(
            request,
            before,
        )

    def test_same_request_same_decision(self):
        request = self.request()

        first = assess_local_forge_execution(
            request
        )
        second = assess_local_forge_execution(
            request
        )

        self.assertEqual(
            first,
            second,
        )


if __name__ == "__main__":
    unittest.main()
