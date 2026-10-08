from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.structure.canonical import canonical_sha256


MODEL_ACQUISITION_PLAN_VERSION = (
    "OX-MODEL-ACQUISITION-PLAN-1"
)

MODEL_ACQUISITION_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-acquisition-plan-1.schema.json"
)


class ModelAcquisitionPlanError(ValueError):
    pass


def load_model_acquisition_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_ACQUISITION_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_model_acquisition_plan(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_acquisition_schema()
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
        raise ModelAcquisitionPlanError(
            f"{location}: {error.message}"
        )

    return value


def build_first_local_model_plan() -> dict[str, Any]:
    plan = {
        "planVersion": MODEL_ACQUISITION_PLAN_VERSION,
        "state": "DECLARED_NOT_ACQUIRED",

        "model": {
            "modelId": "originx.sd15.emaonly",
            "name": "Stable Diffusion v1.5 EMA-only",
            "family": "stable-diffusion-1",
            "version": "1.5",
        },

        "source": {
            "provider": "HUGGING_FACE",
            "repository": "stable-diffusion-v1-5/stable-diffusion-v1-5",
            "revision": "f03de327dd89b501a01da37fc5240cf4fdba85a1",
            "filename": "v1-5-pruned-emaonly.safetensors",
        },

        "artifact": {
            "format": "safetensors",
            "expectedSha256": "sha256:6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa",
            "expectedSizeBytes": 4265146304,
        },

        "runtimeIntent": {
            "runtimeFamily": "stable-diffusion.cpp",
            "requestedTarget": "LOCAL_CPP",
            "runtimeBindingState": "UNBOUND",
        },

        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "selectionGrantsExecutionAuthority": False,
        },
    }

    validate_model_acquisition_plan(plan)
    return plan


def model_acquisition_plan_hash(
    value: dict[str, Any],
) -> str:
    validate_model_acquisition_plan(value)
    return canonical_sha256(value)
