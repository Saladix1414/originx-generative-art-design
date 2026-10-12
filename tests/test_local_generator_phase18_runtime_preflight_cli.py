import json

from oxgad.cli import main


def test_runtime_preflight_cli_emits_blocked_bundle(capsys):
    assert main(["runtime-preflight"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["preflightVersion"] == "OX-RUNTIME-PREFLIGHT-BUNDLE-1"
    assert output["state"] == "BLOCKED_PRE_EXECUTION"
    assert output["adapterHash"].startswith("sha256:")
    assert output["runtimeCommandPlanHash"].startswith("sha256:")
    assert output["runtimePreflightBundleHash"].startswith("sha256:")

    assert output["checks"] == {
        "adapterDeclared": True,
        "commandPlanDeclared": True,
        "commandConstructed": False,
        "runtimeExecutableBound": False,
        "modelArtifactBound": False,
        "executionAuthorized": False,
    }

    assert output["governance"] == {
        "preflightGrantsExecutionAuthority": False,
        "backendInvocationAllowed": False,
        "shellExecutionAllowed": False,
        "networkAccessAllowed": False,
        "modelExecutionAllowed": False,
        "imageGenerationAllowed": False,
    }


def test_runtime_preflight_cli_accepts_metadata_without_execution(capsys):
    assert (
        main(
            [
                "runtime-preflight",
                "--adapter-id",
                "originx.local.test-runtime",
                "--target",
                "LOCAL_GPU",
                "--runtime-family",
                "unknown",
                "--executable-path",
                "/opt/originx/bin/runtime",
                "--runtime-version",
                "0.0-declared",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)

    assert output["state"] == "BLOCKED_PRE_EXECUTION"
    assert output["checks"]["runtimeExecutableBound"] is False
    assert output["checks"]["executionAuthorized"] is False
    assert output["governance"]["backendInvocationAllowed"] is False
    assert output["governance"]["modelExecutionAllowed"] is False
    assert output["governance"]["imageGenerationAllowed"] is False
