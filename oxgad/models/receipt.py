from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from oxgad.models.acquisition import (
    model_acquisition_plan_hash,
    validate_model_acquisition_plan,
)
from oxgad.structure.canonical import canonical_sha256


MODEL_ACQUISITION_RECEIPT_VERSION = (
    "OX-MODEL-ACQUISITION-RECEIPT-1"
)

MODEL_ACQUISITION_RECEIPT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-model-acquisition-receipt-1.schema.json"
)


class ModelAcquisitionReceiptError(ValueError):
    pass


def load_model_acquisition_receipt_schema() -> dict[str, Any]:
    return json.loads(
        MODEL_ACQUISITION_RECEIPT_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def assert_external_model_storage_path(
    artifact_path: Path | str,
    repository_root: Path | str,
) -> Path:
    artifact = Path(artifact_path).expanduser().resolve()
    repository = Path(repository_root).expanduser().resolve()

    if _is_within(artifact, repository):
        raise ModelAcquisitionReceiptError(
            "model artifacts must be stored outside the repository"
        )

    return artifact


def first_local_model_external_path(
    *,
    home: Path | str | None = None,
) -> Path:
    base = (
        Path(home).expanduser()
        if home is not None
        else Path.home()
    )

    return (
        base
        / ".originx"
        / "models"
        / "originx.sd15.emaonly"
        / "f03de327dd89b501a01da37fc5240cf4fdba85a1"
        / "v1-5-pruned-emaonly.safetensors"
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8 * 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)

    return "sha256:" + digest.hexdigest()


def validate_model_acquisition_receipt(
    value: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        load_model_acquisition_receipt_schema()
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
        raise ModelAcquisitionReceiptError(
            f"{location}: {error.message}"
        )

    artifact = value["artifact"]

    if artifact["expectedSha256"] != artifact["observedSha256"]:
        raise ModelAcquisitionReceiptError(
            "receipt artifact hash mismatch"
        )

    if artifact["expectedSizeBytes"] != artifact["observedSizeBytes"]:
        raise ModelAcquisitionReceiptError(
            "receipt artifact size mismatch"
        )

    payload = {
        key: item
        for key, item in value.items()
        if key != "receiptHash"
    }

    if value["receiptHash"] != canonical_sha256(payload):
        raise ModelAcquisitionReceiptError(
            "acquisition receipt hash mismatch"
        )

    return value


def verify_acquired_model_file(
    plan: dict[str, Any],
    artifact_path: Path | str,
    *,
    repository_root: Path | str,
) -> dict[str, Any]:
    acquisition_plan = deepcopy(plan)
    validate_model_acquisition_plan(acquisition_plan)

    artifact_path = assert_external_model_storage_path(
        artifact_path,
        repository_root,
    )

    if artifact_path.name != acquisition_plan["source"]["filename"]:
        raise ModelAcquisitionReceiptError(
            "artifact filename does not match acquisition plan"
        )

    if not artifact_path.is_file():
        raise ModelAcquisitionReceiptError(
            "acquired model artifact does not exist"
        )

    expected_size = acquisition_plan["artifact"]["expectedSizeBytes"]
    observed_size = artifact_path.stat().st_size

    if observed_size != expected_size:
        raise ModelAcquisitionReceiptError(
            "acquired model artifact size mismatch"
        )

    expected_hash = acquisition_plan["artifact"]["expectedSha256"]
    observed_hash = _sha256_file(artifact_path)

    if observed_hash != expected_hash:
        raise ModelAcquisitionReceiptError(
            "acquired model artifact SHA-256 mismatch"
        )

    payload = {
        "receiptVersion": MODEL_ACQUISITION_RECEIPT_VERSION,
        "state": "VERIFIED_ACQUIRED",
        "planHash": model_acquisition_plan_hash(acquisition_plan),
        "model": deepcopy(acquisition_plan["model"]),
        "source": deepcopy(acquisition_plan["source"]),
        "artifact": {
            "format": acquisition_plan["artifact"]["format"],
            "expectedSha256": expected_hash,
            "observedSha256": observed_hash,
            "expectedSizeBytes": expected_size,
            "observedSizeBytes": observed_size,
            "hashMatches": True,
            "sizeMatches": True,
        },
        "storage": {
            "storageClass": "LOCAL_EXTERNAL",
            "filename": artifact_path.name,
        },
        "governance": {
            "acquisitionGrantsTrust": False,
            "acquisitionGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
        },
    }

    receipt = {
        **payload,
        "receiptHash": canonical_sha256(payload),
    }

    validate_model_acquisition_receipt(receipt)
    return receipt
