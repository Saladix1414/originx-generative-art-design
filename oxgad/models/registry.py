from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from oxgad.models.validator import (
    MODEL_REGISTRY_VERSION,
    ModelRegistryValidationError,
    validate_model_registry_record,
)
from oxgad.structure.canonical import canonical_sha256


MODEL_IDENTITY_VERSION = "OX-MODEL-IDENTITY-1"


class ModelRegistryBuildError(ValueError):
    pass


def build_model_identity(
    *,
    model_id: str,
    name: str,
    family: str,
    version: str,
) -> dict[str, str]:
    payload = {
        "identityVersion": MODEL_IDENTITY_VERSION,
        "modelId": model_id,
        "name": name,
        "family": family,
        "version": version,
    }

    return {
        "modelId": model_id,
        "name": name,
        "family": family,
        "version": version,
        "identityHash": canonical_sha256(payload),
    }


def register_model_metadata(
    *,
    model_id: str,
    name: str,
    family: str,
    version: str,
    supported_targets: Iterable[str],
    artifact_sha256: str | None = None,
    artifact_format: str | None = None,
    artifact_size_bytes: int | None = None,
) -> dict[str, Any]:
    artifact_values = (
        artifact_sha256,
        artifact_format,
        artifact_size_bytes,
    )

    supplied = [
        value is not None
        for value in artifact_values
    ]

    if any(supplied) and not all(supplied):
        raise ModelRegistryBuildError(
            "artifact evidence must be supplied together"
        )

    bound = all(supplied)

    record = {
        "registryVersion": MODEL_REGISTRY_VERSION,
        "recordState": "REGISTERED_METADATA_ONLY",
        "modelIdentity": build_model_identity(
            model_id=model_id,
            name=name,
            family=family,
            version=version,
        ),
        "artifact": {
            "bindingState": "HASH_BOUND" if bound else "UNBOUND",
            "sha256": artifact_sha256 if bound else None,
            "format": artifact_format if bound else None,
            "sizeBytes": artifact_size_bytes if bound else None,
        },
        "trust": {
            "state": "UNVERIFIED",
            "evidence": [],
        },
        "capabilities": {
            "purpose": "IMAGE_GENERATION",
            "supportedTargets": list(supported_targets),
            "providerIndependent": True,
        },
        "governance": {
            "registrationGrantsExecutionAuthority": False,
            "trustGrantsExecutionAuthority": False,
            "executionAllowed": False,
        },
    }

    try:
        validate_model_registry_record(record)
    except ModelRegistryValidationError as exc:
        raise ModelRegistryBuildError(
            "invalid model registry metadata"
        ) from exc

    return record
