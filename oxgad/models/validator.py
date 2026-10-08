from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


MODEL_REGISTRY_VERSION = "OX-MODEL-REGISTRY-1"

MODEL_REGISTRY_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-registry-1.schema.json"
)


class ModelRegistryValidationError(ValueError):
    pass


def load_model_registry_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_REGISTRY_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_model_registry_record(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_registry_schema()
    )

    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )

    if errors:
        error = errors[0]
        path = ".".join(
            str(part)
            for part in error.absolute_path
        )
        location = path or "<root>"
        raise ModelRegistryValidationError(
            f"{location}: {error.message}"
        )

    return value


def is_valid_model_registry_record(
    value: dict[str, Any],
) -> bool:
    try:
        validate_model_registry_record(value)
    except ModelRegistryValidationError:
        return False

    return True
