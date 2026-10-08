"""OX-GAD PHASE 1B — OX-ART-SPEC-1 validator tests."""

from __future__ import annotations

import copy
import json
import math
import re
import unittest
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.structure.validator import (
    ART_SPEC_SCHEMA_PATH,
    ArtSpecValidationError,
    get_art_spec_validator,
    is_valid_art_spec,
    load_art_spec_schema,
    validate_art_spec,
)


ROOT = Path(__file__).resolve().parents[1]


def _resolve_ref(
    ref: str,
    root: dict[str, Any],
) -> dict[str, Any]:
    prefix = "#/$defs/"

    if not ref.startswith(prefix):
        raise AssertionError(
            f"Unsupported local schema ref: {ref}"
        )

    name = ref[len(prefix):]

    return root["$defs"][name]


def _matching_string(
    schema: dict[str, Any],
    variant: int,
) -> str:
    minimum = max(
        int(schema.get("minLength", 0)),
        1,
    )

    pattern = schema.get("pattern")

    candidates = [
        f"#{variant + 1:04d}",
        "sha256:" + format(variant, "064x"),
        f"OriginX-{variant + 1}",
        f"value-{variant + 1}",
        "x" * minimum,
    ]

    if pattern is not None:
        regex = re.compile(pattern)

        for candidate in candidates:
            if regex.fullmatch(candidate):
                return candidate

        raise AssertionError(
            "Cannot synthesize value matching "
            f"schema pattern {pattern!r}"
        )

    candidate = candidates[3]

    if len(candidate) < minimum:
        candidate += (
            "x"
            * (minimum - len(candidate))
        )

    maximum = schema.get("maxLength")

    if maximum is not None:
        candidate = candidate[: int(maximum)]

    return candidate


def _minimal_instance(
    schema: dict[str, Any],
    root: dict[str, Any],
    variant: int = 0,
) -> Any:
    if "$ref" in schema:
        return _minimal_instance(
            _resolve_ref(
                schema["$ref"],
                root,
            ),
            root,
            variant,
        )

    if "const" in schema:
        return copy.deepcopy(
            schema["const"]
        )

    if "enum" in schema:
        return copy.deepcopy(
            schema["enum"][
                variant
                % len(schema["enum"])
            ]
        )

    if "oneOf" in schema:
        return _minimal_instance(
            schema["oneOf"][0],
            root,
            variant,
        )

    if "anyOf" in schema:
        return _minimal_instance(
            schema["anyOf"][0],
            root,
            variant,
        )

    if "allOf" in schema:
        result: Any = {}

        for child in schema["allOf"]:
            value = _minimal_instance(
                child,
                root,
                variant,
            )

            if isinstance(
                result,
                dict,
            ) and isinstance(
                value,
                dict,
            ):
                result.update(value)
            else:
                result = value

        return result

    schema_type = schema.get("type")

    if isinstance(schema_type, list):
        schema_type = next(
            item
            for item in schema_type
            if item != "null"
        )

    if schema_type == "object":
        result: dict[str, Any] = {}
        properties = schema.get(
            "properties",
            {},
        )

        for index, field in enumerate(
            schema.get(
                "required",
                [],
            )
        ):
            if field not in properties:
                raise AssertionError(
                    "Required field has no schema: "
                    f"{field}"
                )

            result[field] = _minimal_instance(
                properties[field],
                root,
                variant + index,
            )

        min_properties = int(
            schema.get(
                "minProperties",
                0,
            )
        )

        additional = schema.get(
            "additionalProperties",
            True,
        )

        counter = 0

        while len(result) < min_properties:
            key = f"value{counter + 1}"

            while key in result:
                counter += 1
                key = f"value{counter + 1}"

            if additional is False:
                raise AssertionError(
                    "Schema requires more properties "
                    "than can be generated."
                )

            if isinstance(
                additional,
                dict,
            ):
                result[key] = _minimal_instance(
                    additional,
                    root,
                    variant + counter,
                )
            else:
                result[key] = (
                    f"value-{variant + counter + 1}"
                )

            counter += 1

        return result

    if schema_type == "array":
        count = int(
            schema.get(
                "minItems",
                0,
            )
        )

        item_schema = schema.get(
            "items",
            {},
        )

        return [
            _minimal_instance(
                item_schema,
                root,
                variant + index,
            )
            for index in range(count)
        ]

    if schema_type == "string":
        return _matching_string(
            schema,
            variant,
        )

    if schema_type == "integer":
        value = int(
            schema.get(
                "minimum",
                0,
            )
        )

        if "exclusiveMinimum" in schema:
            value = (
                int(
                    schema["exclusiveMinimum"]
                )
                + 1
            )

        return value

    if schema_type == "number":
        value = float(
            schema.get(
                "minimum",
                0,
            )
        )

        if "exclusiveMinimum" in schema:
            value = (
                float(
                    schema["exclusiveMinimum"]
                )
                + 0.1
            )

        return value

    if schema_type == "boolean":
        return False

    if schema_type == "null":
        return None

    raise AssertionError(
        "Unable to synthesize schema fragment: "
        f"{schema!r}"
    )


def valid_art_spec() -> dict[str, Any]:
    schema = load_art_spec_schema()

    value = _minimal_instance(
        schema,
        schema,
    )

    if not isinstance(value, dict):
        raise AssertionError(
            "Generated Art Spec is not an object."
        )

    return value


class SchemaRuntimeTests(
    unittest.TestCase
):
    def test_schema_path_is_canonical(self):
        self.assertEqual(
            ART_SPEC_SCHEMA_PATH,
            ROOT
            / "schemas"
            / "ox-art-spec-1.schema.json",
        )

    def test_schema_is_draft_2020_12(self):
        schema = load_art_spec_schema()

        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/"
            "draft/2020-12/schema",
        )

        Draft202012Validator.check_schema(
            schema
        )

    def test_runtime_validator_is_draft_2020_12(self):
        self.assertIsInstance(
            get_art_spec_validator(),
            Draft202012Validator,
        )


class ArtSpecValidationTests(
    unittest.TestCase
):
    def test_complete_contract_instance_is_valid(self):
        art_spec = valid_art_spec()

        self.assertIs(
            validate_art_spec(
                art_spec
            ),
            art_spec,
        )

        self.assertTrue(
            is_valid_art_spec(
                art_spec
            )
        )

    def test_missing_identity_is_rejected(self):
        art_spec = valid_art_spec()

        del art_spec["identity"]

        with self.assertRaises(
            ArtSpecValidationError
        ) as context:
            validate_art_spec(
                art_spec
            )

        self.assertIn(
            "identity",
            str(context.exception),
        )

    def test_wrong_spec_version_is_rejected(self):
        art_spec = valid_art_spec()

        art_spec["specVersion"] = (
            "OX-ART-SPEC-999"
        )

        self.assertFalse(
            is_valid_art_spec(
                art_spec
            )
        )

    def test_private_buyer_field_is_rejected(self):
        art_spec = valid_art_spec()

        art_spec["buyerEmail"] = (
            "private@example.invalid"
        )

        with self.assertRaises(
            ArtSpecValidationError
        ) as context:
            validate_art_spec(
                art_spec
            )

        self.assertIn(
            "buyerEmail",
            str(context.exception),
        )

    def test_resonance_remains_narrative_only(self):
        art_spec = valid_art_spec()

        art_spec[
            "resonance"
        ][
            "narrativeOnly"
        ] = False

        self.assertFalse(
            is_valid_art_spec(
                art_spec
            )
        )

    def test_manual_approval_cannot_be_disabled(self):
        art_spec = valid_art_spec()

        art_spec[
            "qualityRequirements"
        ][
            "requireManualApproval"
        ] = False

        self.assertFalse(
            is_valid_art_spec(
                art_spec
            )
        )

    def test_non_mapping_input_is_rejected(self):
        self.assertFalse(
            is_valid_art_spec(
                []
            )
        )

        with self.assertRaises(
            ArtSpecValidationError
        ):
            validate_art_spec(  # type: ignore[arg-type]
                []
            )

    def test_nan_is_rejected_before_hashing(self):
        art_spec = valid_art_spec()

        art_spec[
            "camera"
        ][
            "pitchDegrees"
        ] = math.nan

        with self.assertRaises(
            ArtSpecValidationError
        ):
            validate_art_spec(
                art_spec
            )

    def test_non_string_object_key_is_rejected(self):
        art_spec = valid_art_spec()

        art_spec[
            "identity"
        ][
            "dna"
        ][1] = "invalid"

        with self.assertRaises(
            ArtSpecValidationError
        ):
            validate_art_spec(
                art_spec
            )

    def test_schema_file_remains_valid_json(self):
        data = json.loads(
            ART_SPEC_SCHEMA_PATH.read_text(
                encoding="utf-8",
            )
        )

        self.assertIsInstance(
            data,
            dict,
        )


if __name__ == "__main__":
    unittest.main()
