"""OX-GAD PHASE 1B — canonical OX-ART-SPEC-1 validation."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from oxgad import ART_SPEC_VERSION
from oxgad.structure.canonical import (
    CanonicalizationError,
    canonical_json,
)


ROOT = Path(__file__).resolve().parents[2]

ART_SPEC_SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "ox-art-spec-1.schema.json"
)


class ArtSpecSchemaError(RuntimeError):
    """Raised when the canonical schema itself is invalid."""


class ArtSpecValidationError(ValueError):
    """Raised when data violates OX-ART-SPEC-1."""

    def __init__(
        self,
        errors: Sequence[str],
    ) -> None:
        self.errors = tuple(errors)

        super().__init__(
            "OX-ART-SPEC-1 validation failed:\n- "
            + "\n- ".join(self.errors)
        )


@lru_cache(maxsize=1)
def load_art_spec_schema() -> dict[str, Any]:
    try:
        raw = ART_SPEC_SCHEMA_PATH.read_text(
            encoding="utf-8",
        )
    except OSError as exc:
        raise ArtSpecSchemaError(
            "Unable to read canonical schema: "
            f"{exc}"
        ) from exc

    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ArtSpecSchemaError(
            "Canonical schema is not valid JSON: "
            f"{exc}"
        ) from exc

    if not isinstance(schema, dict):
        raise ArtSpecSchemaError(
            "Canonical schema root must be an object."
        )

    try:
        Draft202012Validator.check_schema(
            schema
        )
    except SchemaError as exc:
        raise ArtSpecSchemaError(
            "Canonical schema is invalid: "
            f"{exc.message}"
        ) from exc

    declared_version = (
        schema
        .get("properties", {})
        .get("specVersion", {})
        .get("const")
    )

    if declared_version != ART_SPEC_VERSION:
        raise ArtSpecSchemaError(
            "Canonical schema version does not match "
            f"{ART_SPEC_VERSION!r}."
        )

    return schema


@lru_cache(maxsize=1)
def get_art_spec_validator() -> Draft202012Validator:
    return Draft202012Validator(
        load_art_spec_schema()
    )


def _format_path(
    path: Sequence[Any],
) -> str:
    result = "$"

    for part in path:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"

    return result


def _format_error(
    error: ValidationError,
) -> str:
    return (
        f"{_format_path(error.absolute_path)}: "
        f"{error.message}"
    )


def _sort_key(
    error: ValidationError,
) -> tuple[str, str]:
    return (
        ".".join(
            str(part)
            for part in error.absolute_path
        ),
        error.message,
    )


def validate_art_spec(
    art_spec: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(art_spec, Mapping):
        raise ArtSpecValidationError(
            (
                "$: Art Spec must be an object.",
            )
        )

    # The schema validator protects the contract.
    # Canonical serialization additionally protects
    # hashing/reproducibility assumptions such as:
    # - finite numeric values
    # - string-only object keys
    # - supported JSON-compatible value types
    try:
        canonical_json(art_spec)
    except CanonicalizationError as exc:
        raise ArtSpecValidationError(
            (
                f"$: {exc}",
            )
        ) from exc

    validator = get_art_spec_validator()

    errors = sorted(
        validator.iter_errors(
            art_spec
        ),
        key=_sort_key,
    )

    if errors:
        raise ArtSpecValidationError(
            tuple(
                _format_error(error)
                for error in errors
            )
        )

    return art_spec


def is_valid_art_spec(
    art_spec: Any,
) -> bool:
    if not isinstance(art_spec, Mapping):
        return False

    try:
        validate_art_spec(
            art_spec
        )
    except ArtSpecValidationError:
        return False

    return True
