import json

from oxgad.cli import main


def test_model_artifact_placement_cli_emits_unplaced_payload(capsys):
    assert main(["model-artifact-placement"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["placementVersion"] == "OX-MODEL-ARTIFACT-PLACEMENT-1"
    assert output["state"] == "UNPLACED"
    assert output["target"] == {
        "directory": "models",
        "filename": "v1-5-pruned-emaonly.safetensors",
        "path": "models/v1-5-pruned-emaonly.safetensors",
    }
    assert output["modelArtifactPlacementHash"].startswith("sha256:")


def test_model_artifact_placement_cli_observes_nothing(capsys):
    assert main(["model-artifact-placement"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["observed"] == {
        "pathExists": False,
        "hashObserved": False,
        "sizeObserved": False,
    }


def test_model_artifact_placement_cli_blocks_authority(capsys):
    assert main(["model-artifact-placement"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "placementGrantsTrust": False,
        "placementGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }
