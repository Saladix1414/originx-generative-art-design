from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import Draft202012Validator

from oxgad.forge.validator import (
    LOCAL_FORGE_VERSION,
    validate_local_forge_request,
)


LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION = (
    "OX-LOCAL-FORGE-EXECUTION-BOUNDARY-1"
)

LOCAL_FORGE_EXECUTION_DECISION_VERSION = (
    "OX-LOCAL-FORGE-EXECUTION-DECISION-1"
)

LOCAL_FORGE_EXECUTION_DECISION_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-local-forge-execution-decision-1.schema.json"
)


class LocalForgeExecutionDecisionValidationError(
    ValueError
):
    pass


class LocalForgeExecutionBlocked(RuntimeError):
    pass


def load_local_forge_execution_decision_schema(
) -> dict[str, Any]:
    return json.loads(
        LOCAL_FORGE_EXECUTION_DECISION_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_local_forge_execution_decision(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_local_forge_execution_decision_schema()
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

        raise LocalForgeExecutionDecisionValidationError(
            f"{location}: {error.message}"
        )

    return value


def assess_local_forge_execution(
    request: dict[str, Any],
) -> dict[str, Any]:
    candidate = deepcopy(request)

    validate_local_forge_request(candidate)

    reasons: list[str] = []

    if (
        candidate["hardware"]["capability"]
        != "CONFIRMED"
    ):
        reasons.append(
            "HARDWARE_CAPABILITY_NOT_CONFIRMED"
        )

    if (
        candidate["model"]["bindingState"]
        != "BOUND"
    ):
        reasons.append("MODEL_UNBOUND")

    if (
        candidate["execution"]["authorizationState"]
        != "AUTHORIZED"
    ):
        reasons.append("AUTHORIZATION_BLOCKED")

    if not candidate["execution"]["executionAllowed"]:
        reasons.append("EXECUTION_NOT_ALLOWED")

    if not candidate["output"]["mediaGenerationAllowed"]:
        reasons.append(
            "MEDIA_GENERATION_NOT_ALLOWED"
        )

    if not candidate["output"]["canonicalArtworkAllowed"]:
        reasons.append(
            "CANONICAL_ARTWORK_NOT_ALLOWED"
        )

    decision = {
        "decisionVersion":
            LOCAL_FORGE_EXECUTION_DECISION_VERSION,
        "boundaryVersion":
            LOCAL_FORGE_EXECUTION_BOUNDARY_VERSION,
        "forgeVersion":
            LOCAL_FORGE_VERSION,
        "requestedTarget":
            candidate["hardware"]["requestedTarget"],
        "capability":
            candidate["hardware"]["capability"],
        "decision":
            "DENY",
        "reasonCodes":
            reasons,
        "backendInvocationAllowed":
            False,
    }

    validate_local_forge_execution_decision(decision)

    return decision


def require_local_forge_execution(
    request: dict[str, Any],
) -> NoReturn:
    decision = assess_local_forge_execution(request)

    raise LocalForgeExecutionBlocked(
        "Local Forge execution blocked: "
        + ",".join(decision["reasonCodes"])
    )
