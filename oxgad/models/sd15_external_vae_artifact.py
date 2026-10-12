"""Verified SD 1.5 external FP16 VAE artifact manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


SCHEMA_PATH = Path(
    "schemas/ox-sd15-external-vae-artifact-1.schema.json"
)
RECEIPT_PATH = Path(
    "docs/local-generator/"
    "phase91-sd15-external-vae-acquisition-receipt.json"
)


def load_external_vae_artifact() -> dict[str, Any]:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def validate_external_vae_artifact(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )
    jsonschema.validate(dict(value), schema)
    return value


__all__ = (
    "load_external_vae_artifact",
    "validate_external_vae_artifact",
)
