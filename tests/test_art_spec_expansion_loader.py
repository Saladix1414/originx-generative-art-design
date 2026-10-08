import json
from pathlib import Path

import pytest

from oxgad.design import (
    expansion_catalog_summary,
    load_art_spec_expansion_catalog,
)


def test_art_spec_expansion_loader_loads_default_catalog():
    catalog = load_art_spec_expansion_catalog()

    assert catalog["schema_version"] == "ox-art-spec-expansion-1"
    assert catalog["project"] == "originx-generative-art-design"
    assert "palette" in catalog["trait_families"]
    assert "canonical" in catalog["render_intents"]


def test_art_spec_expansion_loader_summary_counts():
    catalog = load_art_spec_expansion_catalog()
    summary = expansion_catalog_summary(catalog)

    assert summary == {
        "schema_version": "ox-art-spec-expansion-1",
        "trait_family_count": 10,
        "rarity_band_count": 5,
        "composition_profile_count": 8,
        "render_intent_count": 4,
    }


def test_art_spec_expansion_loader_rejects_invalid_catalog(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "schema_version": "ox-art-spec-expansion-1",
                "project": "originx-generative-art-design",
                "trait_families": ["palette"],
                "rarity_bands": [],
                "composition_profiles": [],
                "render_intents": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        load_art_spec_expansion_catalog(invalid)
