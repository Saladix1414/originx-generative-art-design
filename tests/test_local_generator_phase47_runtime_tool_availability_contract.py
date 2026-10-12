import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.forge.runtime_tool_availability import (
    RUNTIME_TOOL_AVAILABILITY_VERSION,
    build_missing_runtime_tool_availability,
    runtime_tool_availability_hash,
    validate_runtime_tool_availability,
)


def test_runtime_tool_availability_is_schema_valid_and_missing():
    availability = build_missing_runtime_tool_availability()
    schema = json.loads(
        Path("schemas/ox-runtime-tool-availability-1.schema.json").read_text()
    )

    jsonschema.validate(availability, schema)
    validate_runtime_tool_availability(availability)

    assert availability["availabilityVersion"] == (
        RUNTIME_TOOL_AVAILABILITY_VERSION
    )
    assert availability["state"] == "MISSING"
    assert availability["selected"] is None
    assert all(tool["available"] is False for tool in availability["tools"])


def test_runtime_tool_availability_blocks_execution_and_generation():
    availability = build_missing_runtime_tool_availability()

    assert availability["governance"] == {
        "availabilityGrantsExecutionAuthority": False,
        "runtimeInvocationAllowed": False,
        "modelExecutionAllowed": False,
        "mediaGenerationAllowed": False,
    }


def test_runtime_tool_availability_hash_is_deterministic():
    first = build_missing_runtime_tool_availability()
    second = build_missing_runtime_tool_availability()

    assert first == second
    assert first["runtimeToolAvailabilityHash"] == (
        runtime_tool_availability_hash(first)
    )


def test_runtime_tool_availability_rejects_runtime_invocation_authority():
    availability = build_missing_runtime_tool_availability()
    availability["governance"]["runtimeInvocationAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_runtime_tool_availability(availability)


def test_runtime_tool_availability_rejects_hash_tampering():
    availability = build_missing_runtime_tool_availability()
    availability["runtimeToolAvailabilityHash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_runtime_tool_availability(availability)
