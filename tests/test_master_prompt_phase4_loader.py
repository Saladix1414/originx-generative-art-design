import json
from pathlib import Path

import pytest

from oxgad.master_prompt import (
    load_master_prompt_catalog,
    master_prompt_catalog_summary,
)


def test_master_prompt_catalog_loader_loads_default_catalog():
    catalog = load_master_prompt_catalog()

    assert catalog["schema_version"] == "ox-master-prompt-catalog-1"
    assert catalog["project"] == "originx-generative-art-design"
    assert "generic fantasy" in catalog["negative_language"]


def test_master_prompt_catalog_loader_summary_counts():
    catalog = load_master_prompt_catalog()
    summary = master_prompt_catalog_summary(catalog)

    assert summary == {
        "schema_version": "ox-master-prompt-catalog-1",
        "positive_language_count": 8,
        "negative_language_count": 8,
        "camera_language_count": 5,
        "lighting_language_count": 5,
        "material_language_count": 6,
        "macro_detail_count": 3,
        "meso_detail_count": 3,
        "micro_detail_count": 3,
        "forbidden_term_count": 5,
        "required_negative_term_count": 5,
    }


def test_master_prompt_catalog_loader_rejects_invalid_catalog(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "schema_version": "ox-master-prompt-catalog-1",
                "project": "originx-generative-art-design",
                "positive_language": [],
                "negative_language": [],
                "camera_language": [],
                "lighting_language": [],
                "material_language": [],
                "detail_language": {
                    "macro": [],
                    "meso": [],
                    "micro": [],
                },
                "safety_language": {
                    "forbidden_terms": [],
                    "required_negative_terms": [],
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        load_master_prompt_catalog(invalid)
