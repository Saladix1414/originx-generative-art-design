import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.forge.runtime_adapter import build_declared_runtime_adapter
from oxgad.forge.runtime_command_plan import (
    build_declared_runtime_command_plan,
)
from oxgad.forge.runtime_preflight import (
    build_runtime_preflight_bundle,
    runtime_preflight_bundle_hash,
    validate_runtime_preflight_bundle,
)


def _adapter():
    return build_declared_runtime_adapter()


def _command_plan():
    return build_declared_runtime_command_plan(_adapter())


def test_runtime_preflight_bundle_is_schema_valid_and_blocked():
    bundle = build_runtime_preflight_bundle(
        _adapter(),
        _command_plan(),
    )

    schema = json.loads(
        Path("schemas/ox-runtime-preflight-bundle-1.schema.json").read_text()
    )
    jsonschema.validate(bundle, schema)

    assert bundle["preflightVersion"] == "OX-RUNTIME-PREFLIGHT-BUNDLE-1"
    assert bundle["state"] == "BLOCKED_PRE_EXECUTION"
    assert bundle["checks"] == {
        "adapterDeclared": True,
        "commandPlanDeclared": True,
        "commandConstructed": False,
        "runtimeExecutableBound": False,
        "modelArtifactBound": False,
        "executionAuthorized": False,
    }
    assert bundle["governance"] == {
        "preflightGrantsExecutionAuthority": False,
        "backendInvocationAllowed": False,
        "shellExecutionAllowed": False,
        "networkAccessAllowed": False,
        "modelExecutionAllowed": False,
        "imageGenerationAllowed": False,
    }


def test_runtime_preflight_bundle_hash_is_deterministic():
    first = build_runtime_preflight_bundle(
        _adapter(),
        _command_plan(),
    )
    second = build_runtime_preflight_bundle(
        _adapter(),
        _command_plan(),
    )

    assert first == second
    assert first["runtimePreflightBundleHash"] == (
        runtime_preflight_bundle_hash(first)
    )


def test_runtime_preflight_rejects_executable_command():
    command_plan = _command_plan()
    command_plan["command"]["executable"] = "/tmp/runtime"

    with pytest.raises(ValueError, match="executable"):
        build_runtime_preflight_bundle(
            _adapter(),
            command_plan,
        )


def test_runtime_preflight_validation_rejects_hash_tampering():
    bundle = build_runtime_preflight_bundle(
        _adapter(),
        _command_plan(),
    )
    bundle["state"] = "BLOCKED_PRE_EXECUTION"

    bundle["runtimePreflightBundleHash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="hash mismatch"):
        validate_runtime_preflight_bundle(bundle)
