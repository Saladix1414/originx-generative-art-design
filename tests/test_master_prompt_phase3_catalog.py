import json
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator


SCHEMA = Path("schemas/ox-master-prompt-catalog-1.schema.json")
CATALOG = Path("config/master-prompt-catalog.json")


def _schema():
    return json.loads(SCHEMA.read_text())


def _catalog():
    return json.loads(CATALOG.read_text())


def test_master_prompt_catalog_schema_is_valid():
    Draft202012Validator.check_schema(_schema())


def test_master_prompt_catalog_matches_schema():
    jsonschema.validate(_catalog(), _schema())


def test_master_prompt_catalog_contains_originx_art_direction():
    text = CATALOG.read_text().lower()

    for phrase in [
        "dark monumental ancient technological",
        "physically heavy cinematic",
        "structured dragon anatomy",
        "gothic megalithic environment",
        "weathered basalt architecture",
    ]:
        assert phrase in text


def test_master_prompt_catalog_contains_negative_controls():
    catalog = _catalog()

    for term in [
        "generic fantasy",
        "generic cyberpunk",
        "cartoon styling",
        "recognizable franchise design",
        "watermark",
    ]:
        assert term in catalog["negative_language"]


def test_master_prompt_catalog_detail_hierarchy():
    detail = _catalog()["detail_language"]

    assert "anatomy correctness" in detail["macro"]
    assert "scale plates" in detail["meso"]
    assert "surface variation" in detail["micro"]


def test_master_prompt_catalog_is_local_only():
    catalog = _catalog()
    serialized = json.dumps(catalog).lower()

    assert "download" not in serialized
    assert "upload" not in serialized
    assert "api key" not in serialized
    assert "private_key" not in serialized
