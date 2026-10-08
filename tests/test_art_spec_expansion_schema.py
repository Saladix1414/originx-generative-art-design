import json
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("schemas/ox-art-spec-expansion-1.schema.json")


def _valid_expansion():
    return {
        "schema_version": "ox-art-spec-expansion-1",
        "project": "originx-generative-art-design",
        "trait_families": [
            "palette",
            "geometry",
            "material",
            "lighting",
            "depth",
            "motion",
            "symbolic_motif",
            "environment",
            "distortion",
            "finish",
        ],
        "rarity_bands": [
            "common",
            "uncommon",
            "rare",
            "epic",
            "legendary",
        ],
        "composition_profiles": [
            "centered_icon",
            "radial_field",
            "layered_landscape",
            "architectural_stack",
            "orbital_system",
            "fragmented_relic",
            "signal_map",
            "synthetic_organism",
        ],
        "render_intents": [
            "preview",
            "candidate",
            "canonical",
            "high_detail",
        ],
    }


def test_art_spec_expansion_schema_is_valid_json_schema():
    schema = json.loads(SCHEMA_PATH.read_text())

    Draft202012Validator.check_schema(schema)


def test_art_spec_expansion_schema_accepts_planned_catalog():
    schema = json.loads(SCHEMA_PATH.read_text())

    jsonschema.validate(_valid_expansion(), schema)


def test_art_spec_expansion_schema_rejects_unknown_trait_family():
    schema = json.loads(SCHEMA_PATH.read_text())
    payload = _valid_expansion()
    payload["trait_families"] = [
        *payload["trait_families"],
        "unknown_family",
    ]

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))

    assert errors
