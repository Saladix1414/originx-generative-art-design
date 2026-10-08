import json
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator


SCHEMA = Path("schemas/ox-master-prompt-1.schema.json")


def _valid_prompt():
    digest = "a" * 64

    return {
        "schema_version": "ox-master-prompt-1",
        "project": "originx-generative-art-design",
        "prompt_id": "master-prompt-token-0001-preview",
        "source": {
            "identity_input_id": "identity-token-0001",
            "art_spec_hash": digest,
            "render_plan_hash": digest,
        },
        "controlled_vocabulary": {
            "trait_families": [
                "palette",
                "geometry",
                "material",
                "lighting",
            ],
            "rarity_band": "rare",
            "composition_profile": "centered_icon",
            "render_intent": "preview",
        },
        "render_binding": {
            "runtime_target": "LOCAL_CPP",
            "model_requirement": "local diffusion model",
            "seed": 1,
        },
        "prompt": {
            "positive": "monumental dark ancient technological dragon",
            "negative": "watermark, generic fantasy, franchise design",
        },
        "detail_priorities": {
            "macro": ["anatomy", "silhouette", "composition"],
            "meso": ["scales", "armor", "architecture"],
            "micro": ["erosion", "fractures", "surface variation"],
        },
        "safety_boundaries": {
            "local_first": True,
            "no_network": True,
            "no_external_provider_dependency": True,
            "no_uncontrolled_text": True,
            "no_franchise_style": True,
        },
        "provenance_hooks": {
            "catalog_schema_version": "ox-art-spec-expansion-1",
            "prompt_compiler_version": "OX-MASTER-PROMPT-COMPILER-1",
            "hash_required": True,
        },
    }


def test_master_prompt_schema_is_valid_json_schema():
    schema = json.loads(SCHEMA.read_text())

    Draft202012Validator.check_schema(schema)


def test_master_prompt_schema_accepts_valid_payload():
    schema = json.loads(SCHEMA.read_text())

    jsonschema.validate(_valid_prompt(), schema)


def test_master_prompt_schema_requires_local_first_boundaries():
    schema = json.loads(SCHEMA.read_text())
    payload = _valid_prompt()
    payload["safety_boundaries"]["no_network"] = False

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))

    assert errors


def test_master_prompt_schema_rejects_unknown_trait_family():
    schema = json.loads(SCHEMA.read_text())
    payload = _valid_prompt()
    payload["controlled_vocabulary"]["trait_families"].append("unknown")

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))

    assert errors


def test_master_prompt_schema_requires_hashes():
    schema = json.loads(SCHEMA.read_text())
    payload = _valid_prompt()
    payload["source"]["art_spec_hash"] = "not-a-hash"

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))

    assert errors
