from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.models.acquisition import (
    model_acquisition_plan_hash,
    validate_model_acquisition_plan,
)
from oxgad.models.receipt import (
    validate_model_acquisition_receipt,
)
from oxgad.models.registry import (
    register_model_metadata,
)
from oxgad.models.trust import (
    apply_model_trust_evidence,
    assess_model_artifact_evidence,
)
from oxgad.structure.canonical import canonical_sha256


MODEL_ACQUISITION_REGISTRATION_VERSION = (
    "OX-MODEL-ACQUISITION-REGISTRATION-1"
)

MODEL_ACQUISITION_REGISTRATION_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-acquisition-registration-1.schema.json"
)


class ModelAcquisitionRegistrationError(ValueError):
    pass


def load_model_acquisition_registration_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_ACQUISITION_REGISTRATION_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def validate_model_acquisition_registration(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_acquisition_registration_schema()
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
        raise ModelAcquisitionRegistrationError(
            f"{location}: {error.message}"
        )

    payload = {
        key: item
        for key, item in value.items()
        if key != "registrationHash"
    }

    if value["registrationHash"] != canonical_sha256(payload):
        raise ModelAcquisitionRegistrationError(
            "model acquisition registration hash mismatch"
        )

    return value


def promote_verified_acquisition(
    plan: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    acquisition_plan = deepcopy(plan)
    acquisition_receipt = deepcopy(receipt)

    validate_model_acquisition_plan(acquisition_plan)
    validate_model_acquisition_receipt(acquisition_receipt)

    expected_plan_hash = model_acquisition_plan_hash(
        acquisition_plan
    )

    if acquisition_receipt["planHash"] != expected_plan_hash:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt plan hash mismatch"
        )

    if acquisition_receipt["model"] != acquisition_plan["model"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt model mismatch"
        )

    if acquisition_receipt["source"] != acquisition_plan["source"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt source mismatch"
        )

    receipt_artifact = acquisition_receipt["artifact"]
    plan_artifact = acquisition_plan["artifact"]

    if receipt_artifact["format"] != plan_artifact["format"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt format mismatch"
        )

    if receipt_artifact["expectedSha256"] != plan_artifact["expectedSha256"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt expected hash mismatch"
        )

    if receipt_artifact["expectedSizeBytes"] != plan_artifact["expectedSizeBytes"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt expected size mismatch"
        )

    if receipt_artifact["observedSha256"] != plan_artifact["expectedSha256"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt observed hash mismatch"
        )

    if receipt_artifact["observedSizeBytes"] != plan_artifact["expectedSizeBytes"]:
        raise ModelAcquisitionRegistrationError(
            "acquisition receipt observed size mismatch"
        )

    target = acquisition_plan["runtimeIntent"]["requestedTarget"]

    registry_record = register_model_metadata(
        model_id=acquisition_plan["model"]["modelId"],
        name=acquisition_plan["model"]["name"],
        family=acquisition_plan["model"]["family"],
        version=acquisition_plan["model"]["version"],
        supported_targets=[target],
        artifact_sha256=receipt_artifact["observedSha256"],
        artifact_format=receipt_artifact["format"],
        artifact_size_bytes=receipt_artifact["observedSizeBytes"],
    )

    trust_evidence = assess_model_artifact_evidence(
        registry_record,
        observed_sha256=receipt_artifact["observedSha256"],
        observed_format=receipt_artifact["format"],
        observed_size_bytes=receipt_artifact["observedSizeBytes"],
    )

    if trust_evidence["decision"] != "VERIFIED":
        raise ModelAcquisitionRegistrationError(
            "acquired model did not produce VERIFIED trust evidence"
        )

    verified_record = apply_model_trust_evidence(
        registry_record,
        trust_evidence,
    )

    payload = {
        "registrationVersion": MODEL_ACQUISITION_REGISTRATION_VERSION,
        "state": "VERIFIED_REGISTERED",
        "planHash": expected_plan_hash,
        "receiptHash": acquisition_receipt["receiptHash"],
        "model": {
            "registryVersion": verified_record["registryVersion"],
            "modelId": verified_record["modelIdentity"]["modelId"],
            "modelIdentityHash": verified_record["modelIdentity"]["identityHash"],
            "artifactSha256": verified_record["artifact"]["sha256"],
            "artifactSizeBytes": verified_record["artifact"]["sizeBytes"],
            "trustState": verified_record["trust"]["state"],
            "trustEvidenceHash": trust_evidence["evidenceHash"],
        },
        "governance": {
            "registrationGrantsExecutionAuthority": False,
            "trustGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "backendInvocationAllowed": False,
        },
    }

    registration = {
        **payload,
        "registrationHash": canonical_sha256(payload),
    }

    validate_model_acquisition_registration(registration)

    validate_model_acquisition_registration_context(
        acquisition_plan,
        acquisition_receipt,
        registration,
        verified_record,
        trust_evidence,
    )

    return {
        "registration": registration,
        "registryRecord": verified_record,
        "trustEvidence": trust_evidence,
    }


def validate_model_acquisition_registration_context(
    plan: dict[str, Any],
    receipt: dict[str, Any],
    registration: dict[str, Any],
    registry_record: dict[str, Any],
    trust_evidence: dict[str, Any],
) -> dict[str, Any]:
    from oxgad.models.trust import validate_model_trust_evidence
    from oxgad.models.validator import validate_model_registry_record

    acquisition_plan = deepcopy(plan)
    acquisition_receipt = deepcopy(receipt)
    promoted_registration = deepcopy(registration)
    record = deepcopy(registry_record)
    evidence = deepcopy(trust_evidence)

    validate_model_acquisition_plan(acquisition_plan)
    validate_model_acquisition_receipt(acquisition_receipt)
    validate_model_acquisition_registration(promoted_registration)
    validate_model_registry_record(record)
    validate_model_trust_evidence(evidence)

    expected_plan_hash = model_acquisition_plan_hash(
        acquisition_plan
    )

    if acquisition_receipt["planHash"] != expected_plan_hash:
        raise ModelAcquisitionRegistrationError(
            "receipt is not bound to acquisition plan"
        )

    if promoted_registration["planHash"] != expected_plan_hash:
        raise ModelAcquisitionRegistrationError(
            "registration is not bound to acquisition plan"
        )

    if promoted_registration["receiptHash"] != acquisition_receipt["receiptHash"]:
        raise ModelAcquisitionRegistrationError(
            "registration receipt hash mismatch"
        )

    if acquisition_receipt["model"] != acquisition_plan["model"]:
        raise ModelAcquisitionRegistrationError(
            "receipt model context mismatch"
        )

    if acquisition_receipt["source"] != acquisition_plan["source"]:
        raise ModelAcquisitionRegistrationError(
            "receipt source context mismatch"
        )

    artifact = record["artifact"]

    expected_model = {
        "registryVersion": record["registryVersion"],
        "modelId": record["modelIdentity"]["modelId"],
        "modelIdentityHash": record["modelIdentity"]["identityHash"],
        "artifactSha256": artifact["sha256"],
        "artifactSizeBytes": artifact["sizeBytes"],
        "trustState": record["trust"]["state"],
        "trustEvidenceHash": evidence["evidenceHash"],
    }

    if promoted_registration["model"] != expected_model:
        raise ModelAcquisitionRegistrationError(
            "registration model context mismatch"
        )

    if record["trust"]["state"] != "VERIFIED":
        raise ModelAcquisitionRegistrationError(
            "registry record must remain VERIFIED"
        )

    if record["artifact"]["bindingState"] != "HASH_BOUND":
        raise ModelAcquisitionRegistrationError(
            "registry artifact must remain HASH_BOUND"
        )

    if record["trust"]["evidence"] != [evidence["evidenceHash"]]:
        raise ModelAcquisitionRegistrationError(
            "registry trust evidence binding mismatch"
        )

    if evidence["decision"] != "VERIFIED":
        raise ModelAcquisitionRegistrationError(
            "trust evidence must remain VERIFIED"
        )

    if evidence["modelIdentityHash"] != record["modelIdentity"]["identityHash"]:
        raise ModelAcquisitionRegistrationError(
            "trust evidence model identity mismatch"
        )

    expected_artifact = {
        "sha256": artifact["sha256"],
        "format": artifact["format"],
        "sizeBytes": artifact["sizeBytes"],
    }

    if evidence["artifactExpected"] != expected_artifact:
        raise ModelAcquisitionRegistrationError(
            "trust evidence artifact context mismatch"
        )

    if promoted_registration["governance"]["executionAllowed"]:
        raise ModelAcquisitionRegistrationError(
            "registration cannot authorize execution"
        )

    if promoted_registration["governance"]["backendInvocationAllowed"]:
        raise ModelAcquisitionRegistrationError(
            "registration cannot authorize backend invocation"
        )

    return promoted_registration
