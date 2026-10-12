import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.acquisition_path import (
    MODEL_ACQUISITION_PATH_SELECTION_VERSION,
    build_authorized_download_path_selection,
    model_acquisition_path_selection_hash,
    validate_model_acquisition_path_selection,
)


def test_model_acquisition_path_selection_is_schema_valid():
    selection = build_authorized_download_path_selection()
    schema = json.loads(
        Path(
            "schemas/ox-model-acquisition-path-selection-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(selection, schema)
    validate_model_acquisition_path_selection(selection)

    assert selection["selectionVersion"] == (
        MODEL_ACQUISITION_PATH_SELECTION_VERSION
    )
    assert selection["selectedPath"] == "AUTHORIZED_DOWNLOAD"
    assert selection["state"] == "SELECTED_NOT_AUTHORIZED"


def test_model_acquisition_path_selection_does_not_grant_authority():
    selection = build_authorized_download_path_selection()

    assert selection["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "selectionGrantsAcquisitionAuthority": False,
        "selectionGrantsExecutionAuthority": False,
    }


def test_model_acquisition_path_selection_rationale_tracks_missing_dependencies():
    selection = build_authorized_download_path_selection()

    assert selection["rationale"] == {
        "manualPlacementAvailable": False,
        "downloadRequiresExplicitApproval": True,
        "runtimeAvailable": False,
        "modelArtifactPresent": False,
    }


def test_model_acquisition_path_selection_hash_is_deterministic():
    first = build_authorized_download_path_selection()
    second = build_authorized_download_path_selection()

    assert first == second
    assert first["modelAcquisitionPathSelectionHash"] == (
        model_acquisition_path_selection_hash(first)
    )


def test_model_acquisition_path_selection_rejects_download_authority():
    selection = build_authorized_download_path_selection()
    selection["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_model_acquisition_path_selection(selection)
