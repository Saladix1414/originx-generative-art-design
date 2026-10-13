import json
from pathlib import Path

import jsonschema

from oxgad.forge.sd15_external_vae_preflight_plan import (
    APPROVAL_PHRASE,
    build_external_vae_preflight_plan,
)


def test_external_vae_preflight_plan_matches_schema():
    value = build_external_vae_preflight_plan()
    schema = json.loads(
        Path(
            "schemas/"
            "ox-sd15-external-vae-preflight-plan-1.schema.json"
        ).read_text()
    )
    jsonschema.validate(value, schema)


def test_preflight_is_single_and_conservative():
    request = build_external_vae_preflight_plan()["request"]

    assert request["width"] == 256
    assert request["height"] == 256
    assert request["steps"] == 1
    assert request["batchSize"] == 1
    assert request["vaeDecodeMode"] == "NON_TILED"


def test_preflight_binds_verified_external_vae():
    value = build_external_vae_preflight_plan()

    assert value["artifacts"]["vae"]["precision"] == "FP16"
    assert value["artifacts"]["vae"]["sha256"] == (
        "sha256:"
        "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
        "29bb4d81890039d2aa16dd7c"
    )


def test_preflight_requires_separate_approval():
    value = build_external_vae_preflight_plan()

    assert value["approval"]["requiredPhrase"] == APPROVAL_PHRASE
    assert value["approval"]["present"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["genesisRetryAllowed"] is False
