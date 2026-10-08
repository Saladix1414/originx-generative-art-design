import unittest
from copy import deepcopy

from oxgad.forge import (
    LOCAL_FORGE_PREPARATION_VERSION,
    LOCAL_FORGE_VERSION,
    LocalForgePreparationError,
    prepare_local_forge_request,
)
from oxgad.hardware import build_hardware_profile
from tests.test_hardware_detector import observation


HASH = "sha256:" + ("c" * 64)


class LocalForgeContractTests(unittest.TestCase):
    def profile(self):
        return build_hardware_profile(observation())

    def test_versions(self):
        self.assertEqual(
            LOCAL_FORGE_VERSION,
            "OX-LOCAL-FORGE-1",
        )
        self.assertEqual(
            LOCAL_FORGE_PREPARATION_VERSION,
            "OX-LOCAL-FORGE-PREPARATION-1",
        )

    def test_local_cpp_capability_is_bound(self):
        request = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target="LOCAL_CPP",
        )
        self.assertEqual(
            request["hardware"]["capability"],
            "CONFIRMED",
        )

    def test_local_gpu_unknown_is_preserved(self):
        request = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target="LOCAL_GPU",
        )
        self.assertEqual(
            request["hardware"]["capability"],
            "UNKNOWN",
        )

    def test_execution_is_always_blocked(self):
        request = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target="LOCAL_CPP",
        )
        self.assertEqual(
            request["execution"]["mode"],
            "PREPARE_ONLY",
        )
        self.assertEqual(
            request["execution"]["authorizationState"],
            "BLOCKED",
        )
        self.assertFalse(
            request["execution"]["executionAllowed"]
        )
        self.assertFalse(
            request["output"]["mediaGenerationAllowed"]
        )
        self.assertFalse(
            request["output"]["canonicalArtworkAllowed"]
        )

    def test_model_remains_unbound(self):
        request = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=self.profile(),
            requested_target="LOCAL_CPP",
        )
        self.assertEqual(
            request["model"]["bindingState"],
            "UNBOUND",
        )

    def test_same_inputs_same_request(self):
        profile = self.profile()
        first = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=profile,
            requested_target="LOCAL_CPP",
        )
        second = prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=profile,
            requested_target="LOCAL_CPP",
        )
        self.assertEqual(first, second)

    def test_hardware_input_is_not_mutated(self):
        profile = self.profile()
        before = deepcopy(profile)
        prepare_local_forge_request(
            render_plan_hash=HASH,
            hardware_profile=profile,
            requested_target="LOCAL_CPP",
        )
        self.assertEqual(profile, before)

    def test_external_provider_is_rejected(self):
        with self.assertRaises(
            LocalForgePreparationError
        ):
            prepare_local_forge_request(
                render_plan_hash=HASH,
                hardware_profile=self.profile(),
                requested_target="EXTERNAL_PROVIDER",
            )

    def test_invalid_hash_is_rejected(self):
        with self.assertRaises(
            LocalForgePreparationError
        ):
            prepare_local_forge_request(
                render_plan_hash="invalid",
                hardware_profile=self.profile(),
                requested_target="LOCAL_CPP",
            )


if __name__ == "__main__":
    unittest.main()
