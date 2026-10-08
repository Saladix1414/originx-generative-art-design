import json
import unittest
from pathlib import Path

from oxgad.forge import (
    LOCAL_FORGE_BACKEND_VERSION,
    LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION,
    LOCAL_FORGE_EXECUTION_DECISION_VERSION,
    LOCAL_FORGE_PREPARATION_VERSION,
    LOCAL_FORGE_VERSION,
    assess_local_forge_execution,
    prepare_local_forge_request,
)
from oxgad.hardware import build_hardware_profile
from oxgad.structure.canonical import canonical_json
from tests.test_hardware_detector import observation

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "docs" / "architecture" / "phase6-closure.json"

class Phase6ClosureTests(unittest.TestCase):
    def closure(self):
        return json.loads(CLOSURE.read_text(encoding="utf-8"))

    def test_phase_is_complete(self):
        value = self.closure()
        self.assertEqual(value["phase"], 6)
        self.assertEqual(value["status"], "COMPLETE")
        self.assertEqual(value["closureVersion"], "OX-LOCAL-FORGE-CLOSURE-1")

    def test_contract_versions_match_runtime(self):
        value = self.closure()["contracts"]
        self.assertEqual(value["forge"], LOCAL_FORGE_VERSION)
        self.assertEqual(value["preparation"], LOCAL_FORGE_PREPARATION_VERSION)
        self.assertEqual(value["executionBoundary"], LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION)
        self.assertEqual(value["executionDecision"], LOCAL_FORGE_EXECUTION_DECISION_VERSION)
        self.assertEqual(value["backend"], LOCAL_FORGE_BACKEND_VERSION)

    def test_closure_is_canonical_json(self):
        raw = CLOSURE.read_text(encoding="utf-8")
        self.assertEqual(raw, canonical_json(json.loads(raw)))

    def test_execution_remains_disabled(self):
        value = self.closure()
        self.assertEqual(value["executionPolicy"], "LOCAL_FIRST")
        self.assertEqual(value["executionDecision"], "DENY")
        self.assertFalse(value["backendInvocationAllowed"])
        self.assertFalse(value["modelExecutionImplemented"])
        self.assertFalse(value["mediaGenerationImplemented"])
        self.assertFalse(value["canonicalArtworkAllowed"])

    def test_runtime_boundary_still_denies(self):
        profile = build_hardware_profile(observation())
        request = prepare_local_forge_request(
            render_plan_hash="sha256:" + ("a" * 64),
            hardware_profile=profile,
            requested_target="LOCAL_CPP",
        )
        decision = assess_local_forge_execution(request)
        self.assertEqual(decision["decision"], "DENY")
        self.assertFalse(decision["backendInvocationAllowed"])

    def test_next_phase_is_model_registry(self):
        self.assertEqual(
            self.closure()["nextPhase"],
            "PHASE 7 — Model Registry",
        )

if __name__ == "__main__":
    unittest.main()
