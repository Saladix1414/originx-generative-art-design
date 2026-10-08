import json
from pathlib import Path
import re

from oxgad.master_prompt import (
    build_master_prompt_from_art_spec,
    canonical_master_prompt_json,
    master_prompt_hash,
)


ART_SPEC_PATH = Path("output/art-specs/phase2e/token-0001.json")


def _prompt():
    art_spec = json.loads(ART_SPEC_PATH.read_text())
    render_plan = {
        "schemaVersion": "OX-RENDER-1",
        "runtimeTarget": "LOCAL_CPP",
        "modelRequirement": "local diffusion model",
        "seed": art_spec["seed"],
        "positivePrompt": "structured OriginX dragon render plan fixture",
        "negativePrompt": "watermark, broken anatomy, generic fantasy",
    }

    return build_master_prompt_from_art_spec(
        prompt_id="master-prompt-token-0001-candidate",
        identity_input_id="identity-token-0001",
        art_spec=art_spec,
        render_plan=render_plan,
    )


def test_master_prompt_canonical_json_is_stable():
    prompt = _prompt()

    assert canonical_master_prompt_json(prompt) == canonical_master_prompt_json(prompt)


def test_master_prompt_hash_is_sha256_hex():
    digest = master_prompt_hash(_prompt())

    assert re.fullmatch(r"[a-f0-9]{64}", digest)


def test_master_prompt_hash_is_deterministic():
    assert master_prompt_hash(_prompt()) == master_prompt_hash(_prompt())


def test_master_prompt_hash_changes_when_prompt_changes():
    prompt = _prompt()
    changed = json.loads(json.dumps(prompt))
    changed["prompt"]["positive"] += ", altered"

    assert master_prompt_hash(prompt) != master_prompt_hash(changed)
