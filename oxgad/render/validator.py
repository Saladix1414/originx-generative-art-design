"""Validation boundary for OX-RENDER-1."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad import RENDER_VERSION
from oxgad.structure.canonical import canonical_json


RENDER_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-render-1.schema.json"
)


class RenderPlanValidationError(ValueError):
    """Raised when OX-RENDER-1 validation fails."""


def load_render_schema() -> dict[str, Any]:
    schema = json.loads(
        RENDER_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    return schema


def validate_render_plan(
    render_plan: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(render_plan, Mapping):
        raise RenderPlanValidationError(
            "OX-RENDER-1 must be an object."
        )

    value = dict(render_plan)

    if value.get("renderVersion") != RENDER_VERSION:
        raise RenderPlanValidationError(
            "Unexpected render version."
        )

    try:
        canonical_json(value)
    except (TypeError, ValueError) as exc:
        raise RenderPlanValidationError(
            f"Render plan is not canonicalizable: {exc}"
        ) from exc

    validator = Draft202012Validator(
        load_render_schema()
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

        raise RenderPlanValidationError(
            "OX-RENDER-1 validation failed:\n"
            + "\n".join(messages)
        )

    return render_plan


def is_valid_render_plan(
    render_plan: Mapping[str, Any],
) -> bool:
    try:
        validate_render_plan(render_plan)
    except RenderPlanValidationError:
        return False
    return True


__all__ = (
    "RENDER_SCHEMA_PATH",
    "RenderPlanValidationError",
    "is_valid_render_plan",
    "load_render_schema",
    "validate_render_plan",
)
