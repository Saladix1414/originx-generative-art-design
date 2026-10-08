from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


LOCAL_FORGE_BACKEND_VERSION = (
    "OX-LOCAL-FORGE-BACKEND-1"
)

LOCAL_FORGE_BACKEND_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-local-forge-backend-1.schema.json"
)

_LOCAL_TARGET_RUNTIME_KIND = {
    "LOCAL_CPP": "CPP_NATIVE",
    "LOCAL_GPU": "GPU_NATIVE",
}


class LocalForgeBackendValidationError(
    ValueError
):
    pass


def load_local_forge_backend_schema(
) -> dict[str, Any]:
    return json.loads(
        LOCAL_FORGE_BACKEND_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_local_forge_backend(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_local_forge_backend_schema()
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

        raise LocalForgeBackendValidationError(
            f"{location}: {error.message}"
        )

    return value


def declare_local_forge_backend(
    *,
    backend_id: str,
    target: str,
    runtime_name: str | None = None,
    runtime_version: str | None = None,
) -> dict[str, Any]:
    if target not in _LOCAL_TARGET_RUNTIME_KIND:
        raise LocalForgeBackendValidationError(
            "target must be LOCAL_CPP or LOCAL_GPU"
        )

    descriptor = {
        "backendVersion":
            LOCAL_FORGE_BACKEND_VERSION,
        "backendId":
            backend_id,
        "target":
            target,
        "interfaceMode":
            "DECLARED_ONLY",
        "runtime": {
            "kind":
                _LOCAL_TARGET_RUNTIME_KIND[target],
            "name":
                runtime_name,
            "version":
                runtime_version,
        },
        "capabilities": {
            "modelExecutionImplemented":
                False,
            "mediaGenerationImplemented":
                False,
        },
        "governance": {
            "requiresExecutionBoundary":
                True,
            "directInvocationAllowed":
                False,
        },
    }

    validate_local_forge_backend(
        descriptor
    )

    return descriptor



class LocalForgeBackendCompatibilityError(
    ValueError
):
    pass


def validate_local_forge_backend_for_request(
    backend: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    from copy import deepcopy

    from oxgad.forge.validator import (
        validate_local_forge_request,
    )

    descriptor = deepcopy(backend)
    candidate = deepcopy(request)

    validate_local_forge_backend(
        descriptor
    )
    validate_local_forge_request(
        candidate
    )

    if (
        descriptor["target"]
        != candidate["hardware"]["requestedTarget"]
    ):
        raise LocalForgeBackendCompatibilityError(
            "backend target does not match requested target"
        )

    if (
        descriptor["interfaceMode"]
        != "DECLARED_ONLY"
    ):
        raise LocalForgeBackendCompatibilityError(
            "backend interface must remain DECLARED_ONLY"
        )

    if (
        descriptor["governance"][
            "directInvocationAllowed"
        ]
        is not False
    ):
        raise LocalForgeBackendCompatibilityError(
            "direct invocation must remain forbidden"
        )

    return {
        "backendId":
            descriptor["backendId"],
        "target":
            descriptor["target"],
        "compatible":
            True,
        "executionAuthorityGranted":
            False,
        "backendInvocationAllowed":
            False,
    }
