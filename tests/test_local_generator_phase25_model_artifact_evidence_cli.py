import json

from oxgad.cli import main


def test_model_artifact_evidence_cli_emits_missing_evidence(capsys):
    assert main(["model-artifact-evidence"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["evidenceVersion"] == "OX-MODEL-ARTIFACT-EVIDENCE-1"
    assert output["state"] == "MISSING"
    assert output["modelId"] == "originx.sd15.emaonly"
    assert output["modelArtifactEvidenceHash"].startswith("sha256:")

    assert output["observedArtifact"] == {
        "path": None,
        "format": None,
        "sha256": None,
        "sizeBytes": None,
    }


def test_model_artifact_evidence_cli_blocks_trust_execution_and_generation(capsys):
    assert main(["model-artifact-evidence"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["checks"] == {
        "artifactPresent": False,
        "formatMatches": False,
        "hashMatches": False,
        "sizeMatches": False,
    }
    assert output["governance"] == {
        "evidenceGrantsTrust": False,
        "evidenceGrantsExecutionAuthority": False,
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
    }
