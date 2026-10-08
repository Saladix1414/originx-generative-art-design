import json

import jsonschema

from oxgad.master_prompt import build_master_prompt_payload


DIGEST = "a" * 64


def _payload():
    return build_master_prompt_payload(
        prompt_id="master-prompt-token-0001-preview",
        identity_input_id="identity-token-0001",
        art_spec_hash=DIGEST,
        render_plan_hash=DIGEST,
        rarity_band="rare",
        composition_profile="centered_icon",
        render_intent="preview",
        runtime_target="LOCAL_CPP",
        model_requirement="local diffusion model",
        seed=1,
        trait_families=[
            "palette",
            "geometry",
            "material",
            "lighting",
        ],
    )


def test_master_prompt_builder_outputs_schema_valid_payload():
    payload = _payload()

    schema = json.loads(
        open("schemas/ox-master-prompt-1.schema.json", encoding="utf-8").read()
    )

    jsonschema.validate(payload, schema)

    assert payload["schema_version"] == "ox-master-prompt-1"
    assert payload["project"] == "originx-generative-art-design"


def test_master_prompt_builder_is_deterministic():
    assert _payload() == _payload()


def test_master_prompt_builder_sets_local_first_boundaries():
    payload = _payload()

    assert payload["safety_boundaries"] == {
        "local_first": True,
        "no_network": True,
        "no_external_provider_dependency": True,
        "no_uncontrolled_text": True,
        "no_franchise_style": True,
    }


def test_master_prompt_builder_uses_catalog_language():
    payload = _payload()

    assert "dark monumental ancient technological presence" in payload["prompt"]["positive"]
    assert "physically heavy cinematic form" in payload["prompt"]["positive"]
    assert "generic fantasy" in payload["prompt"]["negative"]
    assert "watermark" in payload["prompt"]["negative"]


def test_master_prompt_builder_preserves_detail_hierarchy():
    payload = _payload()

    assert payload["detail_priorities"]["macro"] == [
        "anatomy correctness",
        "silhouette clarity",
        "composition hierarchy",
    ]
    assert payload["detail_priorities"]["meso"] == [
        "scale plates",
        "armor structure",
        "secondary architecture",
    ]
    assert payload["detail_priorities"]["micro"] == [
        "erosion",
        "fractures",
        "surface variation",
    ]
