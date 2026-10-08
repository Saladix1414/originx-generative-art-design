import unittest
from copy import deepcopy

from oxgad.models import (
    MODEL_TRUST_EVIDENCE_VERSION,
    ModelTrustEvidenceError,
    apply_model_trust_evidence,
    assess_model_artifact_evidence,
    register_model_metadata,
)
from oxgad.structure.canonical import canonical_sha256


HASH_A = "sha256:" + ("a" * 64)
HASH_B = "sha256:" + ("b" * 64)


class ModelTrustEvidenceTests(unittest.TestCase):
    def record(self, model_id="originx.test.model", artifact_hash=HASH_A):
        return register_model_metadata(
            model_id=model_id,
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
            supported_targets=["LOCAL_CPP"],
            artifact_sha256=artifact_hash,
            artifact_format="safetensors",
            artifact_size_bytes=4096,
        )

    def evidence(self):
        return assess_model_artifact_evidence(
            self.record(),
            observed_sha256=HASH_A,
            observed_format="safetensors",
            observed_size_bytes=4096,
        )

    def test_version(self):
        self.assertEqual(
            MODEL_TRUST_EVIDENCE_VERSION,
            "OX-MODEL-TRUST-EVIDENCE-1",
        )

    def test_matching_artifact_verifies(self):
        evidence = self.evidence()
        self.assertEqual(evidence["decision"], "VERIFIED")
        self.assertTrue(all(evidence["checks"].values()))

    def test_mismatch_is_rejected(self):
        evidence = assess_model_artifact_evidence(
            self.record(),
            observed_sha256=HASH_B,
            observed_format="safetensors",
            observed_size_bytes=4096,
        )
        self.assertEqual(evidence["decision"], "REJECTED")
        self.assertFalse(evidence["checks"]["hashMatches"])

    def test_same_inputs_same_evidence(self):
        first = self.evidence()
        second = self.evidence()
        self.assertEqual(first, second)

    def test_evidence_hash_tamper_is_rejected(self):
        evidence = self.evidence()
        evidence["evidenceHash"] = HASH_B
        with self.assertRaises(ModelTrustEvidenceError):
            apply_model_trust_evidence(
                self.record(),
                evidence,
            )

    def test_semantic_tamper_is_rejected(self):
        record = self.record()
        evidence = assess_model_artifact_evidence(
            record,
            observed_sha256=HASH_B,
            observed_format="safetensors",
            observed_size_bytes=4096,
        )
        evidence["decision"] = "VERIFIED"
        payload = {
            key: value
            for key, value in evidence.items()
            if key != "evidenceHash"
        }
        evidence["evidenceHash"] = canonical_sha256(payload)
        with self.assertRaises(ModelTrustEvidenceError):
            apply_model_trust_evidence(record, evidence)

    def test_cross_model_replay_is_rejected(self):
        evidence = self.evidence()
        other = self.record(model_id="originx.other.model")
        with self.assertRaises(ModelTrustEvidenceError):
            apply_model_trust_evidence(other, evidence)

    def test_cross_artifact_replay_is_rejected(self):
        evidence = self.evidence()
        other = self.record(artifact_hash=HASH_B)
        with self.assertRaises(ModelTrustEvidenceError):
            apply_model_trust_evidence(other, evidence)

    def test_inputs_are_not_mutated(self):
        record = self.record()
        evidence = self.evidence()
        before_record = deepcopy(record)
        before_evidence = deepcopy(evidence)
        apply_model_trust_evidence(record, evidence)
        self.assertEqual(record, before_record)
        self.assertEqual(evidence, before_evidence)

    def test_verified_still_does_not_authorize(self):
        trusted = apply_model_trust_evidence(
            self.record(),
            self.evidence(),
        )
        self.assertEqual(trusted["trust"]["state"], "VERIFIED")
        self.assertFalse(
            trusted["governance"]["trustGrantsExecutionAuthority"]
        )
        self.assertFalse(
            trusted["governance"]["executionAllowed"]
        )


if __name__ == "__main__":
    unittest.main()
