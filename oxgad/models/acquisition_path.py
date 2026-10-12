"""Model acquisition path selection for local generator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

MODEL_ACQUISITION_PATH_SELECTION_VERSION = (
    "OX-MODEL-ACQUISITION-PATH-SELECTION-1"
)
_SCHEMA_PATH = Path("schemas/ox-model-acquisition-path-selection-1.schema.json")


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def model_acquisition_path_selection_hash(
    selection: Mapping[str, Any],
) -> str:
    payload = dict(selection)
    payload.pop("modelAcquisitionPathSelectionHash", None)
    return "sha256:" + hashlib.sha256(
        _canonical_payload(payload)
    ).hexdigest()


def build_authorized_download_path_selection() -> dict[str, Any]:
    """Select the authorized-download path without granting authority."""
    selection = {
        "selectionVersion": MODEL_ACQUISITION_PATH_SELECTION_VERSION,
        "selectedPath": "AUTHORIZED_DOWNLOAD",
        "state": "SELECTED_NOT_AUTHORIZED",
        "rationale": {
            "manualPlacementAvailable": False,
            "downloadRequiresExplicitApproval": True,
            "runtimeAvailable": False,
            "modelArtifactPresent": False,
        },
        "governance": {
            "downloadAllowed": False,
            "installationAllowed": False,
            "trustGranted": False,
            "executionAllowed": False,
            "mediaGenerationAllowed": False,
            "selectionGrantsAcquisitionAuthority": False,
            "selectionGrantsExecutionAuthority": False,
        },
    }
    selection["modelAcquisitionPathSelectionHash"] = (
        model_acquisition_path_selection_hash(selection)
    )
    validate_model_acquisition_path_selection(selection)
    return selection


def validate_model_acquisition_path_selection(
    selection: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text())
    jsonschema.validate(dict(selection), schema)

    expected_hash = model_acquisition_path_selection_hash(selection)
    if selection["modelAcquisitionPathSelectionHash"] != expected_hash:
        raise ValueError("Model acquisition path selection hash mismatch.")

    return selection
