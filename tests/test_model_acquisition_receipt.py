import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from oxgad.models import (
    MODEL_ACQUISITION_RECEIPT_VERSION,
    ModelAcquisitionReceiptError,
    assert_external_model_storage_path,
    build_first_local_model_plan,
    first_local_model_external_path,
    validate_model_acquisition_receipt,
    verify_acquired_model_file,
)
from oxgad.structure.canonical import canonical_sha256


class ModelAcquisitionReceiptTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(
            MODEL_ACQUISITION_RECEIPT_VERSION,
            "OX-MODEL-ACQUISITION-RECEIPT-1",
        )

    def test_default_storage_is_outside_repository(self):
        root = Path(__file__).resolve().parents[1]
        path = first_local_model_external_path()
        resolved = assert_external_model_storage_path(path, root)
        self.assertEqual(resolved, path.expanduser().resolve())

    def test_repository_storage_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        artifact = root / "models" / "forbidden.safetensors"
        with self.assertRaises(ModelAcquisitionReceiptError):
            assert_external_model_storage_path(artifact, root)

    def test_expected_external_filename(self):
        self.assertEqual(
            first_local_model_external_path().name,
            "v1-5-pruned-emaonly.safetensors",
        )

    def test_missing_artifact_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        plan = build_first_local_model_plan()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / plan["source"]["filename"]
            with self.assertRaises(ModelAcquisitionReceiptError):
                verify_acquired_model_file(
                    plan,
                    path,
                    repository_root=root,
                )

    def test_wrong_size_fails_before_acceptance(self):
        root = Path(__file__).resolve().parents[1]
        plan = build_first_local_model_plan()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / plan["source"]["filename"]
            path.write_bytes(b"not-the-model")
            with self.assertRaises(ModelAcquisitionReceiptError):
                verify_acquired_model_file(
                    plan,
                    path,
                    repository_root=root,
                )

    def test_receipt_hash_tamper_is_rejected(self):
        plan = build_first_local_model_plan()
        payload = {
            "receiptVersion": MODEL_ACQUISITION_RECEIPT_VERSION,
            "state": "VERIFIED_ACQUIRED",
            "planHash": "sha256:" + ("1" * 64),
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
        receipt["receiptHash"] = "sha256:" + ("2" * 64)
        with self.assertRaises(ModelAcquisitionReceiptError):
            validate_model_acquisition_receipt(receipt)

    def test_acquisition_receipt_never_grants_authority(self):
        plan = build_first_local_model_plan()
        self.assertFalse(plan["governance"]["executionAllowed"])
        self.assertFalse(plan["governance"]["mediaGenerationAllowed"])


if __name__ == "__main__":
    unittest.main()
