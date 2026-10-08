import json
import math
import unittest
from pathlib import Path

from oxgad.structure.canonical import (
    CANONICAL_SERIALIZATION_VERSION,
    CanonicalizationError,
    art_spec_hash,
    canonical_json,
    canonical_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "ox-art-spec-1.schema.json"


class SchemaContractTests(unittest.TestCase):
    def test_schema_exists_and_is_valid_json(self):
        data = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(
            data["$id"],
            "urn:originx:ox-gad:schema:ox-art-spec-1",
        )

        self.assertEqual(
            data["properties"]["specVersion"]["const"],
            "OX-ART-SPEC-1",
        )

        self.assertEqual(len(data["required"]), 17)

    def test_resonance_is_explicitly_narrative(self):
        data = json.loads(SCHEMA.read_text(encoding="utf-8"))

        value = (
            data["$defs"]["resonance"]
            ["properties"]["narrativeOnly"]["const"]
        )

        self.assertIs(value, True)

    def test_manual_canonical_approval_is_required(self):
        data = json.loads(SCHEMA.read_text(encoding="utf-8"))

        quality = data["$defs"]["qualityRequirements"]["properties"]

        self.assertIs(
            quality["requireManualApproval"]["const"],
            True,
        )

        self.assertEqual(
            quality["canonicalApprovalMode"]["const"],
            "MANUAL_REQUIRED",
        )


class CanonicalSerializationTests(unittest.TestCase):
    def test_serialization_version(self):
        self.assertEqual(
            CANONICAL_SERIALIZATION_VERSION,
            "OX-CANONICAL-JSON-1",
        )

    def test_key_order_does_not_change_output(self):
        a = {
            "specVersion": "OX-ART-SPEC-1",
            "seed": 42,
            "identity": {
                "tokenId": 1,
                "canonicalName": "Vaerkaion",
            },
        }

        b = {
            "identity": {
                "canonicalName": "Vaerkaion",
                "tokenId": 1,
            },
            "seed": 42,
            "specVersion": "OX-ART-SPEC-1",
        }

        self.assertEqual(
            canonical_json(a),
            canonical_json(b),
        )

        self.assertEqual(
            canonical_sha256(a),
            canonical_sha256(b),
        )

    def test_unicode_normalization_is_stable(self):
        composed = {
            "specVersion": "OX-ART-SPEC-1",
            "name": "Café",
        }

        decomposed = {
            "specVersion": "OX-ART-SPEC-1",
            "name": "Cafe\u0301",
        }

        self.assertEqual(
            canonical_sha256(composed),
            canonical_sha256(decomposed),
        )

    def test_mutation_changes_hash(self):
        original = {
            "specVersion": "OX-ART-SPEC-1",
            "seed": 42,
        }

        mutated = {
            "specVersion": "OX-ART-SPEC-1",
            "seed": 43,
        }

        self.assertNotEqual(
            canonical_sha256(original),
            canonical_sha256(mutated),
        )

    def test_hash_format(self):
        digest = canonical_sha256({"value": 1})

        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(len(digest), 71)

    def test_current_art_spec_version_is_accepted(self):
        digest = art_spec_hash(
            {
                "specVersion": "OX-ART-SPEC-1",
                "seed": 1,
            }
        )

        self.assertTrue(digest.startswith("sha256:"))

    def test_wrong_art_spec_version_is_rejected(self):
        with self.assertRaises(CanonicalizationError):
            art_spec_hash(
                {
                    "specVersion": "OX-ART-SPEC-999",
                    "seed": 1,
                }
            )

    def test_nan_is_rejected(self):
        with self.assertRaises(CanonicalizationError):
            canonical_json({"value": math.nan})

    def test_infinity_is_rejected(self):
        with self.assertRaises(CanonicalizationError):
            canonical_json({"value": math.inf})

    def test_non_string_key_is_rejected(self):
        with self.assertRaises(CanonicalizationError):
            canonical_json({1: "invalid"})

    def test_unicode_key_collision_is_rejected(self):
        with self.assertRaises(CanonicalizationError):
            canonical_json(
                {
                    "Café": 1,
                    "Cafe\u0301": 2,
                }
            )


if __name__ == "__main__":
    unittest.main()
