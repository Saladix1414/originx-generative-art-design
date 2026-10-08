from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


DEFAULT_CATALOG_PATH = Path("config/master-prompt-catalog.json")
DEFAULT_SCHEMA_PATH = Path("schemas/ox-master-prompt-catalog-1.schema.json")


def load_master_prompt_catalog(
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))

    jsonschema.validate(catalog, schema)

    return catalog


def master_prompt_catalog_summary(
    catalog: dict[str, Any],
) -> dict[str, int | str]:
    return {
        "schema_version": catalog["schema_version"],
        "positive_language_count": len(catalog["positive_language"]),
        "negative_language_count": len(catalog["negative_language"]),
        "camera_language_count": len(catalog["camera_language"]),
        "lighting_language_count": len(catalog["lighting_language"]),
        "material_language_count": len(catalog["material_language"]),
        "macro_detail_count": len(catalog["detail_language"]["macro"]),
        "meso_detail_count": len(catalog["detail_language"]["meso"]),
        "micro_detail_count": len(catalog["detail_language"]["micro"]),
        "forbidden_term_count": len(catalog["safety_language"]["forbidden_terms"]),
        "required_negative_term_count": len(
            catalog["safety_language"]["required_negative_terms"]
        ),
    }
