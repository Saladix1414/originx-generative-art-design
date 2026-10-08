"""PHASE 5C deterministic hardware detector tests."""

from __future__ import annotations

import copy
import unittest

from oxgad.hardware import (
    HARDWARE_DETECTOR_VERSION,
    HardwareDetectionError,
    build_hardware_profile,
    validate_hardware_profile,
)


def observation() -> dict:
    return {
        "platform": {
            "system": "Android",
            "release": "16",
            "machine": "aarch64",
            "androidVersion": "16",
            "androidApiLevel": 36,
            "termuxVersion": "0.119.0-beta.3",
        },
        "cpu": {
            "architecture": "aarch64",
            "logicalCores": 8,
            "features": ["asimd", "asimddp"],
            "clusters": [
                {
                    "model": "Cortex-A55",
                    "coreCount": 6,
                    "maxMHz": 2000.0,
                },
                {
                    "model": "Cortex-A78",
                    "coreCount": 2,
                    "maxMHz": 2600.0,
                },
            ],
        },
        "memory": {
            "totalBytes": 5721546752,
            "availableBytes": 1822998528,
            "swapTotalBytes": 8589930496,
            "swapFreeBytes": 6737674240,
        },
        "storage": {
            "path": "/data/user/0",
            "totalBytes": 113816633344,
            "freeBytes": 71940702208,
        },
        "deviceNodes": {
            "/dev/kgsl-3d0": False,
            "/dev/dri/renderD128": False,
            "/dev/dri/card0": True,
        },
        "apiProbes": {
            "vulkan": {
                "toolAvailable": False,
                "probeSucceeded": False,
            },
            "opencl": {
                "toolAvailable": False,
                "probeSucceeded": False,
            },
            "cuda": {
                "toolAvailable": False,
                "probeSucceeded": False,
            },
            "rocm": {
                "toolAvailable": False,
                "probeSucceeded": False,
            },
        },
        "runtimePackages": {
            "torch": False,
            "tensorflow": False,
            "onnxruntime": False,
            "numpy": False,
            "psutil": False,
            "vulkanPython": False,
        },
    }


class HardwareDetectorTests(unittest.TestCase):
    def test_detector_version(self):
        self.assertEqual(
            HARDWARE_DETECTOR_VERSION,
            "OX-HARDWARE-DETECTOR-1",
        )

    def test_same_evidence_same_profile(self):
        source = observation()
        self.assertEqual(
            build_hardware_profile(source),
            build_hardware_profile(source),
        )

    def test_input_is_not_mutated(self):
        source = observation()
        before = copy.deepcopy(source)
        build_hardware_profile(source)
        self.assertEqual(source, before)

    def test_profile_validates(self):
        profile = build_hardware_profile(observation())
        self.assertIs(
            validate_hardware_profile(profile),
            profile,
        )

    def test_local_cpp_is_confirmed(self):
        profile = build_hardware_profile(observation())
        self.assertEqual(
            profile["executionProfiles"]["LOCAL_CPP"]["capability"],
            "CONFIRMED",
        )

    def test_card0_is_not_gpu_proof(self):
        profile = build_hardware_profile(observation())

        nodes = {
            item["path"]: item["presence"]
            for item in profile["accelerators"]["deviceNodes"]
        }

        self.assertEqual(
            nodes["/dev/dri/card0"],
            "PRESENT",
        )
        self.assertEqual(
            profile["executionProfiles"]["LOCAL_GPU"]["capability"],
            "UNKNOWN",
        )

    def test_successful_vulkan_probe_confirms_capability(self):
        source = observation()
        source["apiProbes"]["vulkan"] = {
            "toolAvailable": True,
            "probeSucceeded": True,
        }

        profile = build_hardware_profile(source)

        self.assertEqual(
            profile["accelerators"]["vulkan"]["capability"],
            "CONFIRMED",
        )
        self.assertEqual(
            profile["executionProfiles"]["LOCAL_GPU"]["capability"],
            "CONFIRMED",
        )

    def test_gpu_capability_does_not_enable_execution(self):
        source = observation()
        source["apiProbes"]["vulkan"] = {
            "toolAvailable": True,
            "probeSucceeded": True,
        }

        profile = build_hardware_profile(source)

        self.assertFalse(
            profile["governance"]["executionAllowed"]
        )
        self.assertFalse(
            profile["governance"][
                "hardwareAvailabilityGrantsExecutionAuthority"
            ]
        )

    def test_incomplete_observation_fails_closed(self):
        source = observation()
        del source["memory"]

        with self.assertRaises(HardwareDetectionError):
            build_hardware_profile(source)


if __name__ == "__main__":
    unittest.main()
