import json

from oxgad.cli import main


def test_model_acquisition_plan_cli_emits_declared_refresh(capsys):
    assert main(["model-acquisition-plan"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["refreshVersion"] == "OX-MODEL-ACQUISITION-PLAN-REFRESH-1"
    assert output["state"] == "DECLARED_NOT_ACQUIRED"
    assert output["plan"]["planVersion"] == "OX-MODEL-ACQUISITION-PLAN-1"
    assert output["availability"] == {
        "usableModelArtifactsPresent": False,
        "artifactPathBound": False,
        "artifactHashObserved": False,
        "artifactSizeObserved": False,
    }
    assert output["governance"]["downloadAllowed"] is False
    assert output["governance"]["installationAllowed"] is False
    assert output["governance"]["executionAllowed"] is False
    assert output["governance"]["mediaGenerationAllowed"] is False


def test_model_acquisition_plan_cli_preserves_first_local_model_metadata(capsys):
    assert main(["model-acquisition-plan"]) == 0

    output = json.loads(capsys.readouterr().out)
    plan = output["plan"]

    assert plan["model"]["modelId"] == "originx.sd15.emaonly"
    assert plan["model"]["family"] == "stable-diffusion-1"
    assert plan["runtimeIntent"]["runtimeFamily"] == "stable-diffusion.cpp"
    assert plan["runtimeIntent"]["requestedTarget"] == "LOCAL_CPP"
