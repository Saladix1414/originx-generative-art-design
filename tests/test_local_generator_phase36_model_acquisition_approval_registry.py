import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-model-artifact-acquisition-approval-1.schema.json"


def test_contract_registry_lists_model_acquisition_approval_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert any(
        contract["name"] == "model-acquisition-approval"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"]
        == "ox-model-artifact-acquisition-approval-1.schema.json"
        for contract in output["contracts"]
    )


def test_contract_validation_includes_model_acquisition_approval_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert any(
        result["name"] == "model-acquisition-approval"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in output["results"]
    )


def test_evidence_chain_places_approval_after_authorization(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)
    steps = [item["step"] for item in output["chain"]]

    assert steps.index("model-artifact-authorization") < steps.index(
        "model-acquisition-approval"
    )
