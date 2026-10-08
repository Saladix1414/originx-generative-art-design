import json
from pathlib import Path

from oxgad.master_prompt import (
    build_render_bound_master_prompt,
    master_prompt_hash,
    render_plan_hash,
)
from oxgad.structure.canonical import art_spec_hash


ART_SPEC = Path("output/art-specs/phase2e/token-0001.json")


def _hex_digest(value: str) -> str:
    if value.startswith("sha256:"):
        return value.split(":", 1)[1]

    return value


def _art_spec():
    return json.loads(
        ART_SPEC.read_text()
    )


def _render_plan():
    art_spec = _art_spec()

    return {
        "schemaVersion": "OX-RENDER-1",
        "artSpecHash": _hex_digest(
            art_spec_hash(art_spec)
        ),
        "runtimeTarget": "LOCAL_CPP",
        "seed": art_spec["seed"],
        "resolution": {
            "width": 512,
            "height": 512,
        },
        "sampler": {
            "name": "euler-a",
            "steps": 28,
            "cfgScale": 7.0,
            "scheduler": "normal",
        },
        "modelRequirement": {
            "modelId": "originx-local-test-model",
            "family": "sd-compatible",
            "format": "safetensors",
        },
        "positivePrompt": "monumental ancient technological dragon, cinematic, precise",
        "negativePrompt": "watermark, text artifacts, logo, extra limbs, broken anatomy",
        "detailPasses": [
            {
                "name": "macro",
                "priority": 1,
            },
            {
                "name": "meso",
                "priority": 2,
            },
            {
                "name": "micro",
                "priority": 3,
            },
        ],
        "upscalePlan": {
            "enabled": False,
        },
        "loraPlan": [],
        "controlNetPlan": [],
    }


def test_render_binding_builds_schema_valid_prompt():
    art_spec = _art_spec()
    render_plan = _render_plan()

    payload = build_render_bound_master_prompt(
        prompt_id="master-prompt-token-0001-render-bound",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    assert payload["schema_version"] == "ox-master-prompt-1"
    assert payload["source"]["render_plan_hash"] == render_plan_hash(
        render_plan
    )
    assert payload["source"]["art_spec_hash"] == _hex_digest(
        art_spec_hash(art_spec)
    )
    assert payload["render_binding"]["runtime_target"] == "LOCAL_CPP"
    assert payload["render_binding"]["seed"] == art_spec["seed"]
    assert len(payload["render_binding"]["master_prompt_hash"]) == 64


def test_render_binding_is_deterministic():
    art_spec = _art_spec()
    render_plan = _render_plan()

    first = build_render_bound_master_prompt(
        prompt_id="master-prompt-token-0001-render-bound",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )
    second = build_render_bound_master_prompt(
        prompt_id="master-prompt-token-0001-render-bound",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    assert first == second
    assert master_prompt_hash(first) == master_prompt_hash(second)


def test_render_binding_changes_when_render_plan_changes():
    art_spec = _art_spec()
    render_plan = _render_plan()

    first = build_render_bound_master_prompt(
        prompt_id="master-prompt-token-0001-render-bound",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )

    changed = dict(render_plan)
    changed["seed"] = render_plan["seed"] + 1

    second = build_render_bound_master_prompt(
        prompt_id="master-prompt-token-0001-render-bound",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=changed,
    )

    assert first["source"]["render_plan_hash"] != second["source"]["render_plan_hash"]
    assert first["render_binding"]["seed"] != second["render_binding"]["seed"]
