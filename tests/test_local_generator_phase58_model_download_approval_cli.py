import json

from oxgad.cli import main


def test_model_download_approval_cli_emits_token(capsys):
    assert main(["model-download-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["approvalTokenVersion"] == "OX-MODEL-DOWNLOAD-APPROVAL-TOKEN-1"
    assert output["state"] == "APPROVAL_TOKEN_DECLARED"
    assert output["selectedPath"] == "AUTHORIZED_DOWNLOAD"


def test_model_download_approval_cli_does_not_grant_download(capsys):
    assert main(["model-download-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["approval"]["manualApprovalPresent"] is True
    assert output["approval"]["approvalGrantsDownloadAuthority"] is False
    assert output["governance"]["downloadAllowed"] is False
    assert output["governance"]["executionAllowed"] is False
    assert output["governance"]["mediaGenerationAllowed"] is False


def test_model_download_approval_cli_preserves_target_model(capsys):
    assert main(["model-download-approval"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["targetModel"]["modelId"] == "originx.sd15.emaonly"
    assert output["targetModel"]["filename"] == "v1-5-pruned-emaonly.safetensors"
    assert output["targetModel"]["expectedSizeBytes"] == 4265146304
