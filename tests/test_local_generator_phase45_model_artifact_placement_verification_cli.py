import json

from oxgad.cli import main


def test_model_artifact_placement_verification_cli_emits_missing_payload(capsys):
    assert main(["model-artifact-placement-verification"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["verificationVersion"] == (
        "OX-MODEL-ARTIFACT-PLACEMENT-VERIFICATION-1"
    )
    assert output["state"] == "MISSING"
    assert output["target"] == {
        "path": "models/v1-5-pruned-emaonly.safetensors",
    }
    assert output["modelArtifactPlacementVerificationHash"].startswith(
        "sha256:"
    )


def test_model_artifact_placement_verification_cli_observes_missing_path(capsys):
    assert main(["model-artifact-placement-verification"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["observed"] == {
        "pathExists": False,
        "isFile": False,
        "sizeBytes": None,
    }


def test_model_artifact_placement_verification_cli_blocks_authority(capsys):
    assert main(["model-artifact-placement-verification"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "verificationGrantsTrust": False,
        "verificationGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }
