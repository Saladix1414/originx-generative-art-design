from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.models.validator import (
    validate_model_registry_record,
)
from oxgad.structure.canonical import canonical_sha256


MODEL_TRUST_EVIDENCE_VERSION = "OX-MODEL-TRUST-EVIDENCE-1"

MODEL_TRUST_EVIDENCE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-trust-evidence-1.schema.json"
)


class ModelTrustEvidenceError(ValueError):
    pass


def load_model_trust_evidence_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_TRUST_EVIDENCE_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_model_trust_evidence(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_trust_evidence_schema()
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
        raise ModelTrustEvidenceError(
            f"{location}: {error.message}"
        )
    return value


def assess_model_artifact_evidence(
    record: dict[str, Any],
    *,
    observed_sha256: str,
    observed_format: str,
    observed_size_bytes: int,
) -> dict[str, Any]:
    candidate = deepcopy(record)
    validate_model_registry_record(candidate)

    artifact = candidate["artifact"]
    if artifact["bindingState"] != "HASH_BOUND":
        raise ModelTrustEvidenceError(
            "artifact must be HASH_BOUND before verification"
        )

    checks = {
        "hashMatches": artifact["sha256"] == observed_sha256,
        "formatMatches": artifact["format"] == observed_format,
        "sizeMatches": artifact["sizeBytes"] == observed_size_bytes,
    }

    decision = (
        "VERIFIED"
        if all(checks.values())
        else "REJECTED"
    )

    payload = {
        "evidenceVersion": MODEL_TRUST_EVIDENCE_VERSION,
        "modelIdentityHash": candidate["modelIdentity"]["identityHash"],
        "artifactExpected": {
            "sha256": artifact["sha256"],
            "format": artifact["format"],
            "sizeBytes": artifact["sizeBytes"],
        },
        "artifactObserved": {
            "sha256": observed_sha256,
            "format": observed_format,
            "sizeBytes": observed_size_bytes,
        },
        "checks": checks,
        "decision": decision,
        "governance": {
            "verificationGrantsExecutionAuthority": False,
            "executionAllowed": False,
        },
    }

    evidence = {
        **payload,
        "evidenceHash": canonical_sha256(payload),
    }

    validate_model_trust_evidence(evidence)
    return evidence


def _assert_model_trust_evidence_integrity(
    evidence: dict[str, Any],
) -> None:
    payload = {
        key: value
        for key, value in evidence.items()
        if key != "evidenceHash"
    }

    expected_hash = canonical_sha256(payload)

    if evidence["evidenceHash"] != expected_hash:
        raise ModelTrustEvidenceError(
            "model trust evidence hash mismatch"
        )

    expected = evidence["artifactExpected"]
    observed = evidence["artifactObserved"]

    expected_checks = {
        "hashMatches": expected["sha256"] == observed["sha256"],
        "formatMatches": expected["format"] == observed["format"],
        "sizeMatches": expected["sizeBytes"] == observed["sizeBytes"],
    }

    if evidence["checks"] != expected_checks:
        raise ModelTrustEvidenceError(
            "model trust evidence checks are inconsistent"
        )

    expected_decision = (
        "VERIFIED"
        if all(expected_checks.values())
        else "REJECTED"
    )

    if evidence["decision"] != expected_decision:
        raise ModelTrustEvidenceError(
            "model trust evidence decision is inconsistent"
        )

def apply_model_trust_evidence(
    record: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    candidate = deepcopy(record)
    proof = deepcopy(evidence)

    validate_model_registry_record(candidate)
    validate_model_trust_evidence(proof)
    _assert_model_trust_evidence_integrity(proof)

    if candidate["artifact"]["bindingState"] != "HASH_BOUND":
        raise ModelTrustEvidenceError(
            "registry artifact must remain HASH_BOUND"
        )

    if candidate["modelIdentity"]["identityHash"] != proof["modelIdentityHash"]:
        raise ModelTrustEvidenceError(
            "model identity evidence mismatch"
        )

    expected_artifact = {
        "sha256": candidate["artifact"]["sha256"],
        "format": candidate["artifact"]["format"],
        "sizeBytes": candidate["artifact"]["sizeBytes"],
    }

    if expected_artifact != proof["artifactExpected"]:
        raise ModelTrustEvidenceError(
            "artifact evidence mismatch"
        )

    candidate["trust"] = {
        "state": proof["decision"],
        "evidence": [proof["evidenceHash"]],
    }

    candidate["governance"]["executionAllowed"] = False
    candidate["governance"]["trustGrantsExecutionAuthority"] = False

    validate_model_registry_record(candidate)
    return candidate
