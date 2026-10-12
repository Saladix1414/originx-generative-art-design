import json

from oxgad.cli import main


def test_runtime_adapter_contract_is_registered(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    contracts = {
        item["name"]: item["path"]
        for item in output["contracts"]
    }

    assert (
        contracts["runtime-adapter"]
        == "schemas/ox-runtime-adapter-1.schema.json"
    )


def test_runtime_adapter_contract_validates(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["valid"] is True

    results = {
        item["name"]: item["valid"]
        for item in output["results"]
    }

    assert results["runtime-adapter"] is True


def test_runtime_adapter_is_in_evidence_chain(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    steps = {
        item["step"]: item["schema"]
        for item in output["chain"]
    }

    assert steps["runtime-adapter"] == "ox-runtime-adapter-1.schema.json"


def test_readiness_includes_runtime_adapter_contract(capsys):
    assert main(["readiness"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["ready"] is True
    assert output["contract_count"] == output["evidence_chain_count"]
