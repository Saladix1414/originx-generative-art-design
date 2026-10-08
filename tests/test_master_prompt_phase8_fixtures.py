import json
from pathlib import Path

import jsonschema

from oxgad.master_prompt import master_prompt_hash


FIXTURE_DIR = Path("tests/fixtures/master-prompt")
SCHEMA = Path("schemas/ox-master-prompt-1.schema.json")


def _fixtures():
    return [
        FIXTURE_DIR / "preview.json",
        FIXTURE_DIR / "candidate.json",
        FIXTURE_DIR / "canonical.json",
        FIXTURE_DIR / "high-detail.json",
    ]


def test_master_prompt_fixtures_exist():
    for path in _fixtures():
        assert path.is_file()


def test_master_prompt_fixtures_validate_against_schema():
    schema = json.loads(SCHEMA.read_text())

    for path in _fixtures():
        jsonschema.validate(
            json.loads(path.read_text()),
            schema,
        )


def test_master_prompt_fixtures_cover_render_intents():
    intents = {
        json.loads(path.read_text())["controlled_vocabulary"]["render_intent"]
        for path in _fixtures()
    }

    assert intents == {
        "preview",
        "candidate",
        "canonical",
        "high_detail",
    }


def test_master_prompt_fixtures_are_hashable():
    for path in _fixtures():
        payload = json.loads(path.read_text())
        digest = master_prompt_hash(payload)

        assert len(digest) == 64


def test_master_prompt_fixtures_are_local_only():
    for path in _fixtures():
        text = path.read_text().lower()

        assert "http://" not in text
        assert "https://" not in text
        assert "api key" not in text
        assert "private_key" not in text
