import json

from oxgad.cli import main


def test_model_download_authorization_cli_emits_draft(capsys):
    assert main(["model-download-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["authorizationDraftVersion"] == "OX-MODEL-DOWNLOAD-AUTHORIZATION-DRAFT-1"
    assert output["state"] == "DRAFT_NOT_APPROVED"
    assert output["selectedPath"] == "AUTHORIZED_DOWNLOAD"


def test_model_download_authorization_cli_does_not_grant_download(capsys):
    assert main(["model-download-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["approval"]["manualApprovalRequired"] is True
    assert output["approval"]["manualApprovalPresent"] is False
    assert output["governance"]["downloadAllowed"] is False
    assert output["governance"]["installationAllowed"] is False
    assert output["governance"]["executionAllowed"] is False
    assert output["governance"]["mediaGenerationAllowed"] is False


def test_model_download_authorization_cli_preserves_target_model(capsys):
    assert main(["model-download-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["targetModel"]["modelId"] == "originx.sd15.emaonly"
    assert output["targetModel"]["repository"] == "stable-diffusion-v1-5/stable-diffusion-v1-5"
    assert output["targetModel"]["filename"] == "v1-5-pruned-emaonly.safetensors"
