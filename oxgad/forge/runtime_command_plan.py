"""Runtime command plan contract for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.forge.runtime_adapter import (
    runtime_adapter_hash,
    validate_runtime_adapter,
)
from oxgad.structure.canonical import canonical_sha256


RUNTIME_COMMAND_PLAN_SCHEMA_PATH = Path(
    "schemas/ox-runtime-command-plan-1.schema.json"
)


def _load_runtime_command_plan_schema() -> dict[str, Any]:
    import json

    return json.loads(
        RUNTIME_COMMAND_PLAN_SCHEMA_PATH.read_text()
    )


def build_declared_runtime_command_plan(
    adapter: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executable runtime command plan."""

    validate_runtime_adapter(
        adapter
    )

    plan = {
        "commandPlanVersion": "OX-RUNTIME-COMMAND-PLAN-1",
        "state": "DECLARED_NOT_EXECUTABLE",
        "adapterHash": runtime_adapter_hash(
            adapter
        ),
        "command": {
            "executable": None,
            "argv": [],
            "cwd": None,
            "environment": {},
        },
        "governance": {
            "commandConstructionImplemented": False,
            "backendInvocationAllowed": False,
            "shellAllowed": False,
            "networkAllowed": False,
            "modelExecutionAllowed": False,
        },
    }

    validate_runtime_command_plan(
        plan
    )

    return plan


def validate_runtime_command_plan(
    plan: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate runtime command plan."""

    jsonschema.validate(
        dict(plan),
        _load_runtime_command_plan_schema(),
    )

    return plan


def runtime_command_plan_hash(
    plan: Mapping[str, Any],
) -> str:
    """Return canonical hash for runtime command plan."""

    return canonical_sha256(
        plan
    )
