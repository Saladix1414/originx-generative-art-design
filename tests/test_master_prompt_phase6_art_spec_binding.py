import json
from pathlib import Path

import jsonschema

from oxgad.master_prompt import build_master_prompt_from_art_spec
from oxgad.structure.canonical import art_spec_hash


ART_SPEC_PATH = Path("output/art-specs/phase2e/token-0001.json")


def _hex_digest(value):
    if value.startswith("sha256:"):
        return value.split(":", 1)[1]

    return value


def _art_spec():
    return json.loads(ART_SPEC_PATH.read_text())


def _render_plan():
    art_spec = _art_spec()

    return {
        "schemaVersion": "OX-RENDER-1",
        "runtimeTarget": "LOCAL_CPP",
        "modelRequirement": "local diffusion model",
        "seed": art_spec["seed"],
        "positivePrompt": "structured OriginX dragon render plan fixture",
        "negativePrompt": "watermark, broken anatomy, generic fantasy",
    }


def test_master_prompt_binding_outputs_valid_schema_payload():
    art_spec = _art_spec()
    render_plan = _render_plan()

    payload = build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    schema = json.loads(
        Path("schemas/ox-master-prompt-1.schema.json").read_text()
    )

    jsonschema.validate(payload, schema)

    assert payload["schema_version"] == "ox-master-prompt-1"
    assert payload["source"]["art_spec_hash"] == _hex_digest(art_spec_hash(art_spec))


def test_master_prompt_binding_is_deterministic():
    art_spec = _art_spec()
    render_plan = _render_plan()

    first = build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )
    second = build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    assert first == second


def test_master_prompt_binding_preserves_render_seed():
    art_spec = _art_spec()
    render_plan = _render_plan()

    payload = build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    assert payload["render_binding"]["seed"] == render_plan["seed"]


def test_master_prompt_binding_uses_local_runtime_default():
    art_spec = _art_spec()
    render_plan = _render_plan()

    payload = build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    assert payload["render_binding"]["runtime_target"] == "LOCAL_CPP"
    assert payload["safety_boundaries"]["local_first"] is True
