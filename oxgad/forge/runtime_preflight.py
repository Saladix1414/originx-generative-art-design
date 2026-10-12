"""Declared-only runtime preflight bundle for local generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.forge.runtime_adapter import runtime_adapter_hash
from oxgad.forge.runtime_command_plan import runtime_command_plan_hash

RUNTIME_PREFLIGHT_BUNDLE_VERSION = "OX-RUNTIME-PREFLIGHT-BUNDLE-1"
_SCHEMA_PATH = Path("schemas/ox-runtime-preflight-bundle-1.schema.json")


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def runtime_preflight_bundle_hash(
    bundle: Mapping[str, Any],
) -> str:
    payload = dict(bundle)
    payload.pop("runtimePreflightBundleHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_runtime_preflight_bundle(
    adapter: Mapping[str, Any],
    command_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a blocked pre-execution bundle without invoking any runtime."""
    command = command_plan["command"]
    governance = command_plan["governance"]

    if command["executable"] is not None:
        raise ValueError("Runtime command executable must remain unbound.")
    if command["argv"] != []:
        raise ValueError("Runtime command argv must remain empty.")
    if governance["backendInvocationAllowed"] is not False:
        raise ValueError("Backend invocation must remain blocked.")
    if governance["modelExecutionAllowed"] is not False:
        raise ValueError("Model execution must remain blocked.")

    bundle = {
        "preflightVersion": RUNTIME_PREFLIGHT_BUNDLE_VERSION,
        "state": "BLOCKED_PRE_EXECUTION",
        "adapterHash": runtime_adapter_hash(adapter),
        "runtimeCommandPlanHash": runtime_command_plan_hash(command_plan),
        "checks": {
            "adapterDeclared": True,
            "commandPlanDeclared": True,
            "commandConstructed": False,
            "runtimeExecutableBound": False,
            "modelArtifactBound": False,
            "executionAuthorized": False,
        },
        "governance": {
            "preflightGrantsExecutionAuthority": False,
            "backendInvocationAllowed": False,
            "shellExecutionAllowed": False,
            "networkAccessAllowed": False,
            "modelExecutionAllowed": False,
            "imageGenerationAllowed": False,
        },
    }
    bundle["runtimePreflightBundleHash"] = runtime_preflight_bundle_hash(
        bundle
    )
    validate_runtime_preflight_bundle(bundle)
    return bundle


def validate_runtime_preflight_bundle(
    bundle: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(bundle), schema)

    expected_hash = runtime_preflight_bundle_hash(bundle)
    if bundle["runtimePreflightBundleHash"] != expected_hash:
        raise ValueError("Runtime preflight bundle hash mismatch.")

    return bundle
