import unittest
from copy import deepcopy

from oxgad.models import (
    MODEL_ACQUISITION_REGISTRATION_VERSION,
    ModelAcquisitionRegistrationError,
    build_first_local_model_plan,
    model_acquisition_plan_hash,
    promote_verified_acquisition,
    validate_model_acquisition_receipt,
    validate_model_acquisition_registration,
    validate_model_acquisition_registration_context,
)
from oxgad.structure.canonical import canonical_sha256


class ModelAcquisitionPromotionTests(unittest.TestCase):
    def context(self):
        plan = build_first_local_model_plan()

        payload = {
            "receiptVersion": "OX-MODEL-ACQUISITION-RECEIPT-1",
            "state": "VERIFIED_ACQUIRED",
            "planHash": model_acquisition_plan_hash(plan),
            "model": deepcopy(plan["model"]),
            "source": deepcopy(plan["source"]),
            "artifact": {
                "format": plan["artifact"]["format"],
                "expectedSha256": plan["artifact"]["expectedSha256"],
                "observedSha256": plan["artifact"]["expectedSha256"],
                "expectedSizeBytes": plan["artifact"]["expectedSizeBytes"],
                "observedSizeBytes": plan["artifact"]["expectedSizeBytes"],
                "hashMatches": True,
                "sizeMatches": True,
            },
            "storage": {
                "storageClass": "LOCAL_EXTERNAL",
                "filename": plan["source"]["filename"],
            },
            "governance": {
                "acquisitionGrantsTrust": False,
                "acquisitionGrantsExecutionAuthority": False,
                "executionAllowed": False,
                "mediaGenerationAllowed": False,
            },
        }

        receipt = {
            **payload,
            "receiptHash": canonical_sha256(payload),
        }

        validate_model_acquisition_receipt(receipt)

        promoted = promote_verified_acquisition(
            plan,
            receipt,
        )

        return (
            plan,
            receipt,
            promoted["registration"],
            promoted["registryRecord"],
            promoted["trustEvidence"],
        )

    def rehash_registration(self, value):
        payload = {
            key: item
            for key, item in value.items()
            if key != "registrationHash"
        }
        value["registrationHash"] = canonical_sha256(payload)

    def test_version(self):
        self.assertEqual(
            MODEL_ACQUISITION_REGISTRATION_VERSION,
            "OX-MODEL-ACQUISITION-REGISTRATION-1",
        )

    def test_valid_context_passes(self):
        plan, receipt, registration, record, evidence = self.context()
        validate_model_acquisition_registration_context(
            plan, receipt, registration, record, evidence
        )

    def test_receipt_hash_replay_is_rejected(self):
        plan, receipt, registration, record, evidence = self.context()
        registration["receiptHash"] = "sha256:" + ("9" * 64)
        self.rehash_registration(registration)
        with self.assertRaises(ModelAcquisitionRegistrationError):
            validate_model_acquisition_registration_context(
                plan, receipt, registration, record, evidence
            )

    def test_plan_hash_replay_is_rejected(self):
        plan, receipt, registration, record, evidence = self.context()
        registration["planHash"] = "sha256:" + ("8" * 64)
        self.rehash_registration(registration)
        with self.assertRaises(ModelAcquisitionRegistrationError):
            validate_model_acquisition_registration_context(
                plan, receipt, registration, record, evidence
            )

    def test_cross_model_replay_is_rejected(self):
        plan, receipt, registration, record, evidence = self.context()
        registration["model"]["modelId"] = "originx.other.model"
        self.rehash_registration(registration)
        with self.assertRaises(ModelAcquisitionRegistrationError):
            validate_model_acquisition_registration_context(
                plan, receipt, registration, record, evidence
            )

    def test_cross_evidence_replay_is_rejected(self):
        plan, receipt, registration, record, evidence = self.context()
        registration["model"]["trustEvidenceHash"] = (
            "sha256:" + ("7" * 64)
        )
        self.rehash_registration(registration)
        with self.assertRaises(ModelAcquisitionRegistrationError):
            validate_model_acquisition_registration_context(
                plan, receipt, registration, record, evidence
            )

    def test_receipt_source_replay_is_rejected(self):
        plan, receipt, registration, record, evidence = self.context()
        receipt["source"]["revision"] = "different-revision"
        payload = {
            key: item
            for key, item in receipt.items()
            if key != "receiptHash"
        }
        receipt["receiptHash"] = canonical_sha256(payload)
        registration["receiptHash"] = receipt["receiptHash"]
        self.rehash_registration(registration)
        with self.assertRaises(ModelAcquisitionRegistrationError):
            validate_model_acquisition_registration_context(
                plan, receipt, registration, record, evidence
            )

    def test_inputs_are_not_mutated(self):
        plan, receipt, registration, record, evidence = self.context()
        before = tuple(
            deepcopy(item)
            for item in (
                plan, receipt, registration, record, evidence
            )
        )
        validate_model_acquisition_registration_context(
            plan, receipt, registration, record, evidence
        )
        self.assertEqual(
            (plan, receipt, registration, record, evidence),
            before,
        )

    def test_promotion_never_authorizes_execution(self):
        _, _, registration, _, _ = self.context()
        self.assertFalse(
            registration["governance"]["registrationGrantsExecutionAuthority"]
        )
        self.assertFalse(
            registration["governance"]["trustGrantsExecutionAuthority"]
        )
        self.assertFalse(
            registration["governance"]["executionAllowed"]
        )
        self.assertFalse(
            registration["governance"]["backendInvocationAllowed"]
        )


if __name__ == "__main__":
    unittest.main()
