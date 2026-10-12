"""Runtime tool availability evidence for local generation."""

from __future__ import annotations

import hashlib
import json
import shutil
from typing import Any, Mapping

import jsonschema
from pathlib import Path

RUNTIME_TOOL_AVAILABILITY_VERSION = "OX-RUNTIME-TOOL-AVAILABILITY-1"
_SCHEMA_PATH = Path("schemas/ox-runtime-tool-availability-1.schema.json")
_TOOL_NAMES = (
    "stable-diffusion",
    "stable-diffusion-cli",
    "sd",
    "sd-cli",
    "sd.cpp",
)


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def runtime_tool_availability_hash(
    availability: Mapping[str, Any],
) -> str:
    payload = dict(availability)
    payload.pop("runtimeToolAvailabilityHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_missing_runtime_tool_availability() -> dict[str, Any]:
    """Observe runtime tool names without invoking them."""
    tools = []
    for name in _TOOL_NAMES:
        found = shutil.which(name)
        if found is not None:
            raise ValueError(
                "Runtime tool availability expected missing tools."
            )
        tools.append(
            {
                "name": name,
                "available": False,
                "path": None,
            }
        )

    availability = {
        "availabilityVersion": RUNTIME_TOOL_AVAILABILITY_VERSION,
        "state": "MISSING",
        "tools": tools,
        "selected": None,
        "governance": {
            "availabilityGrantsExecutionAuthority": False,
            "runtimeInvocationAllowed": False,
            "modelExecutionAllowed": False,
            "mediaGenerationAllowed": False,
        },
    }
    availability["runtimeToolAvailabilityHash"] = (
        runtime_tool_availability_hash(availability)
    )
    validate_runtime_tool_availability(availability)
    return availability


def validate_runtime_tool_availability(
    availability: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(availability), schema)

    expected_hash = runtime_tool_availability_hash(availability)
    if availability["runtimeToolAvailabilityHash"] != expected_hash:
        raise ValueError("Runtime tool availability hash mismatch.")

    return availability
