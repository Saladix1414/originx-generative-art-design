import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-model-download-approval-token-1.schema.json"


def test_contract_registry_lists_model_download_approval_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert any(
        contract["name"] == "model-download-approval"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"] == "ox-model-download-approval-token-1.schema.json"
        for contract in output["contracts"]
    )


def test_contract_validation_includes_model_download_approval_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert any(
        result["name"] == "model-download-approval"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in output["results"]
    )


def test_evidence_chain_places_download_approval_after_download_authorization(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)
    steps = [item["step"] for item in output["chain"]]

    assert steps.index("model-download-approval") == (
        steps.index("model-download-authorization") + 1
    )
