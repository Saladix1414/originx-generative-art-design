from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
import json
import re
from typing import Any

_SCHEMA_VERSION = "ox-provenance-manifest-1"
_PROJECT = "originx-generative-art-design"
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _require_sha256(name: str, value: str) -> str:
    value = _require_text(name, value)
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase sha256 hex digest")
    return value


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build_provenance_manifest(
    *,
    art_spec_id: str,
    identity_input_id: str,
    model_registry_id: str,
    model_binding_id: str,
    render_request_id: str,
    render_backend_id: str,
    output_artifact_id: str,
    output_sha256: str,
    phase: str = "phase8",
    created_at: str | None = None,
) -> dict[str, Any]:
    created_at = created_at or datetime.now(UTC).replace(microsecond=0).isoformat()

    manifest: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _require_text("phase", phase),
        "created_at": _require_text("created_at", created_at),
        "inputs": {
            "art_spec_id": _require_text("art_spec_id", art_spec_id),
            "identity_input_id": _require_text("identity_input_id", identity_input_id),
        },
        "model": {
            "registry_id": _require_text("model_registry_id", model_registry_id),
            "binding_id": _require_text("model_binding_id", model_binding_id),
        },
        "render": {
            "request_id": _require_text("render_request_id", render_request_id),
            "backend_id": _require_text("render_backend_id", render_backend_id),
        },
        "output": {
            "artifact_id": _require_text("output_artifact_id", output_artifact_id),
            "sha256": _require_sha256("output_sha256", output_sha256),
        },
        "integrity": {
            "manifest_sha256": "",
        },
    }

    unsigned = deepcopy(manifest)
    unsigned["integrity"]["manifest_sha256"] = ""
    manifest["integrity"]["manifest_sha256"] = sha256(_canonical_bytes(unsigned)).hexdigest()

    return manifest


def verify_provenance_manifest(manifest: dict[str, Any]) -> bool:
    expected = deepcopy(manifest)
    current_digest = expected.get("integrity", {}).get("manifest_sha256")

    if not isinstance(current_digest, str):
        return False

    expected["integrity"]["manifest_sha256"] = ""
    recalculated = sha256(_canonical_bytes(expected)).hexdigest()

    return current_digest == recalculated
