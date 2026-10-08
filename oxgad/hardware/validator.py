"""Validation boundary for OX-HARDWARE-PROFILE-1."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.hardware import HARDWARE_PROFILE_VERSION
from oxgad.structure.canonical import canonical_json


HARDWARE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-hardware-profile-1.schema.json"
)


class HardwareProfileValidationError(ValueError):
    """Raised when hardware capability evidence is invalid."""


def load_hardware_schema() -> dict[str, Any]:
    schema = json.loads(
        HARDWARE_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    return schema


def validate_hardware_profile(
    profile: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(profile, Mapping):
        raise HardwareProfileValidationError(
            "Hardware profile must be an object."
        )

    value = dict(profile)

    if value.get("profileVersion") != HARDWARE_PROFILE_VERSION:
        raise HardwareProfileValidationError(
            "Unexpected hardware profile version."
        )

    try:
        canonical_json(value)
    except (TypeError, ValueError) as exc:
        raise HardwareProfileValidationError(
            f"Hardware profile is not canonicalizable: {exc}"
        ) from exc

    validator = Draft202012Validator(
        load_hardware_schema()
    )

    errors = sorted(
        validator.iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )

    if errors:
        messages = []
        for error in errors:
            path = ".".join(
                str(part)
                for part in error.absolute_path
            )
            location = path or "<root>"
            messages.append(
                f"{location}: {error.message}"
            )

        raise HardwareProfileValidationError(
            "OX-HARDWARE-PROFILE-1 validation failed:\n"
            + "\n".join(messages)
        )

    return profile


def is_valid_hardware_profile(
    profile: Mapping[str, Any],
) -> bool:
    try:
        validate_hardware_profile(profile)
    except HardwareProfileValidationError:
        return False
    return True


__all__ = (
    "HARDWARE_SCHEMA_PATH",
    "HardwareProfileValidationError",
    "is_valid_hardware_profile",
    "load_hardware_schema",
    "validate_hardware_profile",
)
