from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


LOCAL_FORGE_VERSION = "OX-LOCAL-FORGE-1"

LOCAL_FORGE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-local-forge-1.schema.json"
)


class LocalForgeValidationError(ValueError):
    pass


def load_local_forge_schema() -> dict[str, Any]:
    return json.loads(
        LOCAL_FORGE_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_local_forge_request(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_local_forge_schema()
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

        raise LocalForgeValidationError(
            f"{location}: {error.message}"
        )

    return value


def is_valid_local_forge_request(
    value: dict[str, Any],
) -> bool:
    try:
        validate_local_forge_request(value)
    except LocalForgeValidationError:
        return False

    return True
