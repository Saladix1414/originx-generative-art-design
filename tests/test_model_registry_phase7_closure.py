import json
import unittest
from pathlib import Path

from oxgad.models import (
    MODEL_BINDING_VERSION,
    MODEL_IDENTITY_VERSION,
    MODEL_REGISTRY_VERSION,
    MODEL_TRUST_EVIDENCE_VERSION,
)
from oxgad.structure.canonical import canonical_json

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "docs" / "architecture" / "phase7-closure.json"

class Phase7ClosureTests(unittest.TestCase):
    def closure(self):
        return json.loads(CLOSURE.read_text(encoding="utf-8"))

    def test_phase_complete(self):
        value = self.closure()
        self.assertEqual(value["phase"], 7)
        self.assertEqual(value["status"], "COMPLETE")
        self.assertEqual(value["closureVersion"], "OX-MODEL-REGISTRY-CLOSURE-1")

    def test_contract_versions(self):
        value = self.closure()["contracts"]
        self.assertEqual(value["registry"], MODEL_REGISTRY_VERSION)
        self.assertEqual(value["identity"], MODEL_IDENTITY_VERSION)
        self.assertEqual(value["trustEvidence"], MODEL_TRUST_EVIDENCE_VERSION)
        self.assertEqual(value["binding"], MODEL_BINDING_VERSION)

    def test_canonical_json(self):
        raw = CLOSURE.read_text(encoding="utf-8")
        self.assertEqual(raw, canonical_json(json.loads(raw)))

    def test_authority_separation(self):
        value = self.closure()
        self.assertFalse(value["registrationGrantsExecutionAuthority"])
        self.assertFalse(value["trustGrantsExecutionAuthority"])
        self.assertFalse(value["bindingGrantsExecutionAuthority"])
        self.assertFalse(value["executionAllowed"])
        self.assertFalse(value["backendInvocationAllowed"])

    def test_supported_targets(self):
        self.assertEqual(
            self.closure()["supportedTargets"],
            ["LOCAL_CPP", "LOCAL_GPU"],
        )

    def test_next_phase(self):
        self.assertEqual(
            self.closure()["nextPhase"],
            "PHASE 8 — First Local Model",
        )

if __name__ == "__main__":
    unittest.main()
