import json
from pathlib import Path

import jsonschema


CATALOG = Path("config/art-spec-expansion-catalog.json")
SCHEMA = Path("schemas/ox-art-spec-expansion-1.schema.json")


def _catalog():
    return json.loads(CATALOG.read_text())


def test_art_spec_expansion_catalog_matches_schema():
    jsonschema.validate(
        _catalog(),
        json.loads(SCHEMA.read_text()),
    )


def test_art_spec_expansion_catalog_has_expected_counts():
    catalog = _catalog()

    assert len(catalog["trait_families"]) == 10
    assert len(catalog["rarity_bands"]) == 5
    assert len(catalog["composition_profiles"]) == 8
    assert len(catalog["render_intents"]) == 4


def test_art_spec_expansion_catalog_has_unique_values():
    catalog = _catalog()

    for key in [
        "trait_families",
        "rarity_bands",
        "composition_profiles",
        "render_intents",
    ]:
        values = catalog[key]
        assert len(values) == len(set(values))


def test_art_spec_expansion_catalog_is_local_only():
    text = CATALOG.read_text().lower()

    assert "http://" not in text
    assert "https://" not in text
    assert "download" not in text
    assert "upload" not in text
