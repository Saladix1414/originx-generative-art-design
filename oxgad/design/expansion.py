from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


DEFAULT_CATALOG_PATH = Path("config/art-spec-expansion-catalog.json")
DEFAULT_SCHEMA_PATH = Path("schemas/ox-art-spec-expansion-1.schema.json")


def load_art_spec_expansion_catalog(
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))

    jsonschema.validate(catalog, schema)

    return catalog


def expansion_catalog_summary(
    catalog: dict[str, Any],
) -> dict[str, int | str]:
    return {
        "schema_version": catalog["schema_version"],
        "trait_family_count": len(catalog["trait_families"]),
        "rarity_band_count": len(catalog["rarity_bands"]),
        "composition_profile_count": len(catalog["composition_profiles"]),
        "render_intent_count": len(catalog["render_intents"]),
    }
