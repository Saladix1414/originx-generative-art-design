from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.forge import validate_local_forge_request
from oxgad.models.validator import validate_model_registry_record
from oxgad.structure.canonical import canonical_sha256


MODEL_BINDING_VERSION = "OX-MODEL-BINDING-1"

MODEL_BINDING_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-binding-1.schema.json"
)


class ModelBindingError(ValueError):
    pass


def load_model_binding_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_BINDING_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_model_binding(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_binding_schema()
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
        raise ModelBindingError(
            f"{location}: {error.message}"
        )

    payload = {
        key: item
        for key, item in value.items()
        if key != "bindingHash"
    }

    if value["bindingHash"] != canonical_sha256(payload):
        raise ModelBindingError(
            "model binding hash mismatch"
        )

    return value


def bind_verified_model_to_local_forge(
    record: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    model = deepcopy(record)
    forge_request = deepcopy(request)

    validate_model_registry_record(model)
    validate_local_forge_request(forge_request)

    if model["trust"]["state"] != "VERIFIED":
        raise ModelBindingError(
            "model must be VERIFIED before binding"
        )

    if model["artifact"]["bindingState"] != "HASH_BOUND":
        raise ModelBindingError(
            "model artifact must be HASH_BOUND"
        )

    evidence = model["trust"]["evidence"]

    if len(evidence) != 1:
        raise ModelBindingError(
            "exactly one trust evidence hash is required"
        )

    target = forge_request["hardware"]["requestedTarget"]

    if target not in model["capabilities"]["supportedTargets"]:
        raise ModelBindingError(
            "model does not support requested local target"
        )

    payload = {
        "bindingVersion": MODEL_BINDING_VERSION,
        "bindingState": "VERIFIED_MODEL_BOUND",
        "source": {
            "forgeVersion": forge_request["forgeVersion"],
            "renderPlanHash": forge_request["source"]["renderPlanHash"],
            "requestedTarget": target,
        },
        "model": {
            "registryVersion": model["registryVersion"],
            "modelId": model["modelIdentity"]["modelId"],
            "modelIdentityHash": model["modelIdentity"]["identityHash"],
            "artifactSha256": model["artifact"]["sha256"],
            "trustState": "VERIFIED",
            "trustEvidenceHash": evidence[0],
        },
        "compatibility": {
            "targetSupported": True,
        },
        "governance": {
            "bindingGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "backendInvocationAllowed": False,
        },
    }

    binding = {
        **payload,
        "bindingHash": canonical_sha256(payload),
    }

    validate_model_binding(binding)

    return binding


def validate_model_binding_for_local_forge(
    binding: dict[str, Any],
    record: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    proof = deepcopy(binding)
    model = deepcopy(record)
    forge_request = deepcopy(request)

    validate_model_binding(proof)
    validate_model_registry_record(model)
    validate_local_forge_request(forge_request)

    if model["trust"]["state"] != "VERIFIED":
        raise ModelBindingError(
            "bound model must remain VERIFIED"
        )

    if model["artifact"]["bindingState"] != "HASH_BOUND":
        raise ModelBindingError(
            "bound model artifact must remain HASH_BOUND"
        )

    if len(model["trust"]["evidence"]) != 1:
        raise ModelBindingError(
            "bound model trust evidence is ambiguous"
        )

    expected = {
        "renderPlanHash": forge_request["source"]["renderPlanHash"],
        "requestedTarget": forge_request["hardware"]["requestedTarget"],
        "modelId": model["modelIdentity"]["modelId"],
        "modelIdentityHash": model["modelIdentity"]["identityHash"],
        "artifactSha256": model["artifact"]["sha256"],
        "trustEvidenceHash": model["trust"]["evidence"][0],
    }

    actual = {
        "renderPlanHash": proof["source"]["renderPlanHash"],
        "requestedTarget": proof["source"]["requestedTarget"],
        "modelId": proof["model"]["modelId"],
        "modelIdentityHash": proof["model"]["modelIdentityHash"],
        "artifactSha256": proof["model"]["artifactSha256"],
        "trustEvidenceHash": proof["model"]["trustEvidenceHash"],
    }

    if actual != expected:
        raise ModelBindingError(
            "model binding context mismatch"
        )

    if expected["requestedTarget"] not in model["capabilities"]["supportedTargets"]:
        raise ModelBindingError(
            "bound model no longer supports requested target"
        )

    return proof
