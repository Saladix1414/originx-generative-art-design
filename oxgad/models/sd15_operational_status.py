"""Authoritative operational rejection for OX-MODEL-002."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


SCHEMA_PATH = Path(
    "schemas/ox-sd15-operational-status-1.schema.json"
)
STATUS_PATH = Path(
    "docs/local-generator/"
    "phase96-sd15-operational-status.json"
)


def load_sd15_operational_status() -> dict[str, Any]:
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def validate_sd15_operational_status(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )
    jsonschema.validate(dict(value), schema)
    return value


__all__ = (
    "load_sd15_operational_status",
    "validate_sd15_operational_status",
)
