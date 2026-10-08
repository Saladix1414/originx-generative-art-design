import unittest

from oxgad.models import (
    MODEL_IDENTITY_VERSION,
    MODEL_REGISTRY_VERSION,
    ModelRegistryBuildError,
    build_model_identity,
    register_model_metadata,
    validate_model_registry_record,
)


class ModelRegistryFoundationTests(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(MODEL_IDENTITY_VERSION, "OX-MODEL-IDENTITY-1")
        self.assertEqual(MODEL_REGISTRY_VERSION, "OX-MODEL-REGISTRY-1")

    def test_same_identity_same_hash(self):
        kwargs = dict(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
        )
        self.assertEqual(
            build_model_identity(**kwargs),
            build_model_identity(**kwargs),
        )

    def test_version_changes_identity_hash(self):
        first = build_model_identity(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
        )
        second = build_model_identity(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="2.0",
        )
        self.assertNotEqual(first["identityHash"], second["identityHash"])

    def test_unbound_registration(self):
        value = register_model_metadata(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
            supported_targets=["LOCAL_CPP"],
        )
        validate_model_registry_record(value)
        self.assertEqual(value["artifact"]["bindingState"], "UNBOUND")
        self.assertIsNone(value["artifact"]["sha256"])

    def test_hash_bound_registration(self):
        value = register_model_metadata(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
            supported_targets=["LOCAL_CPP", "LOCAL_GPU"],
            artifact_sha256="sha256:" + ("5" * 64),
            artifact_format="safetensors",
            artifact_size_bytes=4096,
        )
        validate_model_registry_record(value)
        self.assertEqual(value["artifact"]["bindingState"], "HASH_BOUND")

    def test_registration_is_unverified(self):
        value = register_model_metadata(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
            supported_targets=["LOCAL_CPP"],
        )
        self.assertEqual(value["trust"]["state"], "UNVERIFIED")
        self.assertEqual(value["trust"]["evidence"], [])

    def test_registration_never_authorizes_execution(self):
        value = register_model_metadata(
            model_id="originx.test.model",
            name="OriginX Test Model",
            family="test-family",
            version="1.0",
            supported_targets=["LOCAL_CPP"],
        )
        self.assertFalse(value["governance"]["registrationGrantsExecutionAuthority"])
        self.assertFalse(value["governance"]["trustGrantsExecutionAuthority"])
        self.assertFalse(value["governance"]["executionAllowed"])

    def test_partial_artifact_evidence_is_rejected(self):
        with self.assertRaises(ModelRegistryBuildError):
            register_model_metadata(
                model_id="originx.test.model",
                name="OriginX Test Model",
                family="test-family",
                version="1.0",
                supported_targets=["LOCAL_CPP"],
                artifact_sha256="sha256:" + ("6" * 64),
            )

    def test_external_provider_is_rejected(self):
        with self.assertRaises(ModelRegistryBuildError):
            register_model_metadata(
                model_id="originx.test.model",
                name="OriginX Test Model",
                family="test-family",
                version="1.0",
                supported_targets=["EXTERNAL_PROVIDER"],
            )


if __name__ == "__main__":
    unittest.main()
