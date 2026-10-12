import json

from oxgad.cli import main


def test_runtime_command_plan_cli_emits_declared_non_executable_plan(capsys):
    assert main(["runtime-command-plan"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["commandPlanVersion"] == "OX-RUNTIME-COMMAND-PLAN-1"
    assert output["state"] == "DECLARED_NOT_EXECUTABLE"
    assert output["adapterHash"].startswith("sha256:")
    assert output["runtimeCommandPlanHash"].startswith("sha256:")

    assert output["command"] == {
        "executable": None,
        "argv": [],
        "cwd": None,
        "environment": {},
    }

    assert output["governance"] == {
        "commandConstructionImplemented": False,
        "backendInvocationAllowed": False,
        "shellAllowed": False,
        "networkAllowed": False,
        "modelExecutionAllowed": False,
    }


def test_runtime_command_plan_cli_accepts_adapter_metadata_without_execution(capsys):
    assert (
        main(
            [
                "runtime-command-plan",
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

    assert output["commandPlanVersion"] == "OX-RUNTIME-COMMAND-PLAN-1"
    assert output["state"] == "DECLARED_NOT_EXECUTABLE"
    assert output["command"]["executable"] is None
    assert output["command"]["argv"] == []
    assert output["governance"]["backendInvocationAllowed"] is False
    assert output["governance"]["shellAllowed"] is False
    assert output["governance"]["modelExecutionAllowed"] is False
