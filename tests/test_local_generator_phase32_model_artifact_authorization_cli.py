import json

from oxgad.cli import main


def test_model_artifact_authorization_cli_emits_blocked_authorization(capsys):
    assert main(["model-artifact-authorization"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["authorizationVersion"] == (
        "OX-MODEL-ARTIFACT-ACQUISITION-AUTHORIZATION-1"
    )
    assert output["state"] == "BLOCKED_PENDING_MANUAL_APPROVAL"
    assert output["source"]["decision"] == "BLOCKED_NO_ARTIFACT"
    assert output["modelArtifactAcquisitionAuthorizationHash"].startswith(
        "sha256:"
    )


def test_model_artifact_authorization_cli_requires_missing_manual_approval(capsys):
    assert main(["model-artifact-authorization"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["authorization"] == {
        "manualApprovalRequired": True,
        "manualApprovalPresent": False,
        "approvedBy": None,
        "approvalTimestamp": None,
    }


def test_model_artifact_authorization_cli_blocks_download_execution_and_generation(capsys):
    assert main(["model-artifact-authorization"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "authorizationGrantsAcquisitionAuthority": False,
        "authorizationGrantsExecutionAuthority": False,
    }
