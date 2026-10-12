"""Execution decision binding for OriginX Local Forge."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.structure.canonical import canonical_sha256


DECISION_SCHEMA_PATH = Path(
    "schemas/ox-local-forge-execution-decision-1.schema.json"
)


def _load_decision_schema() -> dict[str, Any]:
    import json

    return json.loads(
        DECISION_SCHEMA_PATH.read_text()
    )


def build_execution_decision(
    forge_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a schema-valid deny decision from an OX-LOCAL-FORGE-1 contract."""

    execution = forge_contract["execution"]
    hardware = forge_contract["hardware"]
    model = forge_contract["model"]
    output = forge_contract["output"]

    reason_codes: list[str] = []

    if hardware["capability"] != "CONFIRMED":
        reason_codes.append(
            "HARDWARE_CAPABILITY_NOT_CONFIRMED"
        )

    if model["bindingState"] != "VERIFIED_MODEL_BOUND":
        reason_codes.append(
            "MODEL_UNBOUND"
        )

    if execution["authorizationState"] != "AUTHORIZED":
        reason_codes.append(
            "AUTHORIZATION_BLOCKED"
        )

    if execution["executionAllowed"] is not True:
        reason_codes.append(
            "EXECUTION_NOT_ALLOWED"
        )

    if output["mediaGenerationAllowed"] is not True:
        reason_codes.append(
            "MEDIA_GENERATION_NOT_ALLOWED"
        )

    if output["canonicalArtworkAllowed"] is not True:
        reason_codes.append(
            "CANONICAL_ARTWORK_NOT_ALLOWED"
        )

    decision = {
        "decisionVersion": "OX-LOCAL-FORGE-EXECUTION-DECISION-1",
        "boundaryVersion": "OX-LOCAL-FORGE-EXECUTION-BOUNDARY-1",
        "forgeVersion": forge_contract["forgeVersion"],
        "requestedTarget": hardware["requestedTarget"],
        "capability": hardware["capability"],
        "decision": "DENY",
        "reasonCodes": sorted(
            set(reason_codes)
        ),
        "backendInvocationAllowed": False,
    }

    validate_execution_decision(
        decision
    )

    return decision


def validate_execution_decision(
    decision: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate an execution decision against the contract schema."""

    jsonschema.validate(
        dict(decision),
        _load_decision_schema(),
    )

    return decision


def execution_decision_hash(
    decision: Mapping[str, Any],
) -> str:
    """Return canonical hash for an execution decision."""

    return canonical_sha256(
        decision
    )
