import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-master-prompt-evidence-chain-1.schema.json"


def test_contract_registry_lists_prompt_chain_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    contracts = output["contracts"]

    assert any(
        contract["name"] == "master-prompt-chain"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"]
        == "ox-master-prompt-evidence-chain-1.schema.json"
        for contract in contracts
    )


def test_contract_validation_includes_prompt_chain_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["valid"] is True

    results = output["results"]

    assert any(
        result["name"] == "master-prompt-chain"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in results
    )
