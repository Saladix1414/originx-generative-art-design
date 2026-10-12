import json

from oxgad.cli import main


def test_model_download_final_authorization_cli_emits_blocked_gate(capsys):
    assert main(["model-download-final-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["finalAuthorizationVersion"] == "OX-MODEL-DOWNLOAD-FINAL-AUTHORIZATION-1"
    assert output["state"] == "BLOCKED_PENDING_REQUIRED_CHECKS"
    assert output["selectedPath"] == "AUTHORIZED_DOWNLOAD"


def test_model_download_final_authorization_cli_reports_pending_checks(capsys):
    assert main(["model-download-final-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)
    checks = output["blockingChecks"]
    assert checks["licenseReviewCompleted"] is False
    assert checks["storageCheckCompleted"] is False
    assert checks["runtimeCompatibilityChecked"] is False
    assert checks["hashVerificationPlanned"] is True


def test_model_download_final_authorization_cli_does_not_grant_authority(capsys):
    assert main(["model-download-final-authorization"]) == 0
    output = json.loads(capsys.readouterr().out)
    governance = output["governance"]
    assert governance["downloadAllowed"] is False
    assert governance["installationAllowed"] is False
    assert governance["executionAllowed"] is False
    assert governance["mediaGenerationAllowed"] is False
    assert governance["finalGateGrantsAuthority"] is False
