import json

from oxgad.cli import main


def test_runtime_tool_availability_cli_emits_missing_payload(capsys):
    assert main(["runtime-tool-availability"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["availabilityVersion"] == "OX-RUNTIME-TOOL-AVAILABILITY-1"
    assert output["state"] == "MISSING"
    assert output["selected"] is None
    assert output["runtimeToolAvailabilityHash"].startswith("sha256:")
    assert all(tool["available"] is False for tool in output["tools"])


def test_runtime_tool_availability_cli_reports_expected_tool_names(capsys):
    assert main(["runtime-tool-availability"]) == 0

    output = json.loads(capsys.readouterr().out)
    names = [tool["name"] for tool in output["tools"]]

    assert names == [
        "stable-diffusion",
        "stable-diffusion-cli",
        "sd",
        "sd-cli",
        "sd.cpp",
    ]


def test_runtime_tool_availability_cli_blocks_execution_and_generation(capsys):
    assert main(["runtime-tool-availability"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["governance"] == {
        "availabilityGrantsExecutionAuthority": False,
        "runtimeInvocationAllowed": False,
        "modelExecutionAllowed": False,
        "mediaGenerationAllowed": False,
    }
