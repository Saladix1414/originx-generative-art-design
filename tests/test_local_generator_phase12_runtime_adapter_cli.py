import json

from oxgad.cli import main


def test_runtime_adapter_cli_outputs_declared_adapter(capsys):
    assert main(["runtime-adapter"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["adapterVersion"] == "OX-RUNTIME-ADAPTER-1"
    assert output["adapterId"] == "originx.local_cpp.stable_diffusion_cpp"
    assert output["target"] == "LOCAL_CPP"
    assert output["runtime"]["family"] == "stable-diffusion.cpp"
    assert output["runtime"]["executablePath"] is None
    assert output["interfaceMode"] == "DECLARED_ONLY"
    assert output["capabilities"]["commandConstructionImplemented"] is False
    assert output["governance"]["backendInvocationAllowed"] is False
    assert output["runtimeAdapterHash"].startswith("sha256:")


def test_runtime_adapter_cli_accepts_declared_metadata(capsys):
    assert (
        main(
            [
                "runtime-adapter",
                "--adapter-id",
                "originx.local_cpp.test_runtime",
                "--target",
                "LOCAL_CPP",
                "--runtime-family",
                "unknown",
                "--executable-path",
                "/usr/local/bin/test-runtime",
                "--runtime-version",
                "0.0.0",
            ]
        )
        == 0
    )

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["adapterId"] == "originx.local_cpp.test_runtime"
    assert output["runtime"]["family"] == "unknown"
    assert output["runtime"]["executablePath"] == "/usr/local/bin/test-runtime"
    assert output["runtime"]["version"] == "0.0.0"
    assert output["governance"]["directInvocationAllowed"] is False
