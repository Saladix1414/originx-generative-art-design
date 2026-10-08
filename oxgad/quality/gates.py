from __future__ import annotations

import re
from typing import Any

_SCHEMA_VERSION = "ox-quality-gate-report-1"
_PROJECT = "originx-generative-art-design"
_PHASE = "phase9"
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _has_text(value: object) -> bool:
    return bool(_text(value).strip())


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))


def _gate(gate_id: str, passed: bool, severity: str, message: str) -> dict[str, str]:
    return {
        "id": gate_id,
        "status": "pass" if passed else "fail",
        "severity": severity,
        "message": message,
    }


def evaluate_quality_gates(
    *,
    candidate_id: str,
    provenance_manifest: dict[str, Any],
    art_spec: dict[str, Any],
) -> dict[str, Any]:
    manifest_integrity = provenance_manifest.get("integrity", {})
    manifest_sha = manifest_integrity.get("manifest_sha256")

    output = provenance_manifest.get("output", {})
    model = provenance_manifest.get("model", {})
    render = provenance_manifest.get("render", {})

    gates = [
        _gate(
            "candidate-id-present",
            _has_text(candidate_id),
            "required",
            "Candidate id must be present.",
        ),
        _gate(
            "provenance-integrity-present",
            _valid_sha256(manifest_sha),
            "required",
            "Provenance manifest must expose a valid integrity digest.",
        ),
        _gate(
            "output-hash-present",
            _valid_sha256(output.get("sha256")),
            "required",
            "Output artifact must be bound to a SHA-256 digest.",
        ),
        _gate(
            "model-binding-present",
            _has_text(model.get("registry_id")) and _has_text(model.get("binding_id")),
            "required",
            "Candidate must be bound to a registry model and binding id.",
        ),
        _gate(
            "render-backend-present",
            _has_text(render.get("request_id")) and _has_text(render.get("backend_id")),
            "required",
            "Candidate must be bound to a local forge render request and backend.",
        ),
        _gate(
            "art-spec-identity-present",
            _has_text(art_spec.get("token_id")) or _has_text(art_spec.get("id")),
            "required",
            "Art spec must include a stable token id or id.",
        ),
        _gate(
            "art-spec-has-rules",
            bool(art_spec.get("rules") or art_spec.get("traits") or art_spec.get("composition")),
            "advisory",
            "Art spec should include rules, traits, or composition evidence.",
        ),
    ]

    failed_required = [
        gate["id"]
        for gate in gates
        if gate["status"] == "fail" and gate["severity"] == "required"
    ]

    failed_advisory = [
        gate["id"]
        for gate in gates
        if gate["status"] == "fail" and gate["severity"] == "advisory"
    ]

    required_passed = not failed_required

    return {
        "schema_version": _SCHEMA_VERSION,
        "project": _PROJECT,
        "phase": _PHASE,
        "candidate_id": candidate_id,
        "provenance_manifest_sha256": manifest_sha if isinstance(manifest_sha, str) else "",
        "gates": gates,
        "summary": {
            "passed": required_passed,
            "required_passed": required_passed,
            "failed_required": failed_required,
            "failed_advisory": failed_advisory,
        },
    }
