import json
import unittest
from pathlib import Path

from oxgad.hardware import (
    HARDWARE_DETECTOR_VERSION,
    HARDWARE_PROFILE_VERSION,
    build_hardware_profile,
    load_hardware_schema,
)
from oxgad.structure.canonical import canonical_json, canonical_sha256
from tests.test_hardware_detector import observation

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "architecture" / "phase5d-hardware-evidence.json"
CLOSURE = ROOT / "docs" / "architecture" / "phase5-closure.json"


class Phase5ClosureTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.closure = json.loads(CLOSURE.read_text(encoding="utf-8"))

    def test_closure_contract(self):
        self.assertEqual(self.closure["phase"], 5)
        self.assertEqual(self.closure["status"], "COMPLETE")
        self.assertEqual(self.closure["closureVersion"], "OX-HARDWARE-CLOSURE-1")
        self.assertEqual(self.closure["hardwareProfileVersion"], HARDWARE_PROFILE_VERSION)
        self.assertEqual(self.closure["hardwareDetectorVersion"], HARDWARE_DETECTOR_VERSION)

    def test_canonical_and_hash_bindings(self):
        self.assertEqual(
            CLOSURE.read_text(encoding="utf-8"),
            canonical_json(self.closure),
        )
        self.assertEqual(
            self.closure["hardwareSchemaHash"],
            canonical_sha256(load_hardware_schema()),
        )
        self.assertEqual(
            self.closure["hardwareEvidenceManifestHash"],
            canonical_sha256(self.evidence),
        )
        payload = {
            key: value
            for key, value in self.evidence.items()
            if key != "evidenceHash"
        }
        self.assertEqual(
            self.evidence["evidenceHash"],
            canonical_sha256(payload),
        )

    def test_determinism_and_gpu_boundary(self):
        first = build_hardware_profile(observation())
        second = build_hardware_profile(observation())
        self.assertEqual(first, second)
        nodes = {
            item["path"]: item["presence"]
            for item in first["accelerators"]["deviceNodes"]
        }
        self.assertEqual(nodes["/dev/dri/card0"], "PRESENT")
        self.assertEqual(
            first["executionProfiles"]["LOCAL_GPU"]["capability"],
            "UNKNOWN",
        )

    def test_governance(self):
        self.assertEqual(self.closure["executionPolicy"], "LOCAL_FIRST")
        self.assertFalse(
            self.closure["hardwareAvailabilityGrantsExecutionAuthority"]
        )
        self.assertFalse(self.closure["executionAllowed"])

    def test_volatile_fields_and_next_phase(self):
        self.assertEqual(
            self.closure["excludedVolatileFields"],
            [
                "memory.availableBytes",
                "memory.swapFreeBytes",
                "storage.freeBytes",
            ],
        )
        self.assertEqual(
            self.closure["nextPhase"],
            "PHASE 6 — OriginX Local Forge",
        )


if __name__ == "__main__":
    unittest.main()
