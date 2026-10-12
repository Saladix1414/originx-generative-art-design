import json

from oxgad.cli import main


def test_model_acquisition_path_cli_emits_selected_not_authorized(capsys):
    assert main(["model-acquisition-path"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["selectionVersion"] == (
        "OX-MODEL-ACQUISITION-PATH-SELECTION-1"
    )
    assert output["selectedPath"] == "AUTHORIZED_DOWNLOAD"
    assert output["state"] == "SELECTED_NOT_AUTHORIZED"
    assert output["modelAcquisitionPathSelectionHash"].startswith("sha256:")


def test_model_acquisition_path_cli_tracks_missing_dependencies(capsys):
    assert main(["model-acquisition-path"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["rationale"] == {
        "manualPlacementAvailable": False,
        "downloadRequiresExplicitApproval": True,
        "runtimeAvailable": False,
        "modelArtifactPresent": False,
    }


def test_model_acquisition_path_cli_does_not_grant_authority(capsys):
    assert main(["model-acquisition-path"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "selectionGrantsAcquisitionAuthority": False,
        "selectionGrantsExecutionAuthority": False,
    }
