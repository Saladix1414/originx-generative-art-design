import json

from oxgad.cli import main


def test_model_artifact_decision_cli_emits_blocked_decision(capsys):
    assert main(["model-artifact-decision"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["decisionVersion"] == (
        "OX-MODEL-ARTIFACT-ACQUISITION-DECISION-1"
    )
    assert output["decision"] == "BLOCKED_NO_ARTIFACT"
    assert output["source"]["artifactEvidenceState"] == "MISSING"
    assert output["modelArtifactAcquisitionDecisionHash"].startswith("sha256:")


def test_model_artifact_decision_cli_blocks_download_execution_and_generation(capsys):
    assert main(["model-artifact-decision"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "trustGranted": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "decisionGrantsAcquisitionAuthority": False,
        "decisionGrantsExecutionAuthority": False,
    }
    assert output["reasonCodes"] == [
        "MODEL_ARTIFACT_MISSING",
        "DOWNLOAD_NOT_AUTHORIZED",
        "INSTALLATION_NOT_AUTHORIZED",
        "TRUST_NOT_GRANTED",
        "EXECUTION_NOT_AUTHORIZED",
    ]
