import json

from oxgad.cli import main


def test_model_acquisition_approval_cli_emits_draft(capsys):
    assert main(["model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["approvalVersion"] == (
        "OX-MODEL-ARTIFACT-ACQUISITION-APPROVAL-1"
    )
    assert output["state"] == "DRAFT_NOT_APPROVED"
    assert output["source"]["authorizationState"] == (
        "BLOCKED_PENDING_MANUAL_APPROVAL"
    )
    assert output["modelArtifactAcquisitionApprovalHash"].startswith("sha256:")


def test_model_acquisition_approval_cli_does_not_approve(capsys):
    assert main(["model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["approval"] == {
        "approved": False,
        "approvedBy": None,
        "approvalTimestamp": None,
        "approvalScope": "MODEL_ARTIFACT_ACQUISITION_ONLY",
    }


def test_model_acquisition_approval_cli_blocks_download_execution_and_generation(capsys):
    assert main(["model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "approvalGrantsAcquisitionAuthority": False,
        "approvalGrantsExecutionAuthority": False,
    }
