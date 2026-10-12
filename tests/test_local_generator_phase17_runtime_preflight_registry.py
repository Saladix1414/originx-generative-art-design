import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-runtime-preflight-bundle-1.schema.json"


def test_contract_registry_lists_runtime_preflight_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert any(
        contract["name"] == "runtime-preflight-bundle"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"]
        == "ox-runtime-preflight-bundle-1.schema.json"
        for contract in output["contracts"]
    )


def test_contract_validation_includes_runtime_preflight_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True

    assert any(
        result["name"] == "runtime-preflight-bundle"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in output["results"]
    )


def test_evidence_chain_includes_runtime_preflight_after_command_plan(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)
    steps = [item["step"] for item in output["chain"]]

    assert steps[-2:] == [
        "runtime-command-plan",
        "runtime-preflight-bundle",
    ]
