import json

from oxgad.cli import main


def test_explicit_model_acquisition_approval_cli_emits_not_granted(capsys):
    assert main(["explicit-model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["explicitApprovalVersion"] == (
        "OX-EXPLICIT-MODEL-ACQUISITION-APPROVAL-1"
    )
    assert output["state"] == "NOT_GRANTED"
    assert output["explicitModelAcquisitionApprovalHash"].startswith(
        "sha256:"
    )


def test_explicit_model_acquisition_approval_cli_requires_exact_user_approval(capsys):
    assert main(["explicit-model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["approvalIntent"] == {
        "requiresExactUserApproval": True,
        "approvalPhrase": None,
        "approvalRecorded": False,
    }


def test_explicit_model_acquisition_approval_cli_blocks_all_authority(capsys):
    assert main(["explicit-model-acquisition-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "explicitApprovalGrantsAcquisitionAuthority": False,
        "explicitApprovalGrantsExecutionAuthority": False,
    }
