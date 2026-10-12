"""Runtime adapter descriptors for Local Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jsonschema

from oxgad.structure.canonical import canonical_sha256


RUNTIME_ADAPTER_SCHEMA_PATH = Path(
    "schemas/ox-runtime-adapter-1.schema.json"
)


def _load_runtime_adapter_schema() -> dict[str, Any]:
    import json

    return json.loads(
        RUNTIME_ADAPTER_SCHEMA_PATH.read_text()
    )


def build_declared_runtime_adapter(
    *,
    adapter_id: str = "originx.local_cpp.stable_diffusion_cpp",
    target: str = "LOCAL_CPP",
    runtime_family: str = "stable-diffusion.cpp",
    executable_path: str | None = None,
    runtime_version: str | None = None,
) -> dict[str, Any]:
    """Build a declared-only runtime adapter descriptor."""

    adapter = {
        "adapterVersion": "OX-RUNTIME-ADAPTER-1",
        "adapterId": adapter_id,
        "target": target,
        "runtime": {
            "family": runtime_family,
            "executablePath": executable_path,
            "version": runtime_version,
        },
        "interfaceMode": "DECLARED_ONLY",
        "capabilities": {
            "modelExecutionImplemented": False,
            "mediaGenerationImplemented": False,
            "commandConstructionImplemented": False,
        },
        "governance": {
            "directInvocationAllowed": False,
            "backendInvocationAllowed": False,
            "requiresExecutionDecision": True,
            "requiresModelBinding": True,
            "requiresCandidateProvenance": True,
        },
    }

    validate_runtime_adapter(
        adapter
    )

    return adapter


def validate_runtime_adapter(
    adapter: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate runtime adapter descriptor."""

    jsonschema.validate(
        dict(adapter),
        _load_runtime_adapter_schema(),
    )

    return adapter


def runtime_adapter_hash(
    adapter: Mapping[str, Any],
) -> str:
    """Return canonical hash for a runtime adapter descriptor."""

    return canonical_sha256(
        adapter
    )
