import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-model-acquisition-path-selection-1.schema.json"


def test_contract_registry_lists_model_acquisition_path_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert any(
        contract["name"] == "model-acquisition-path"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"] == "ox-model-acquisition-path-selection-1.schema.json"
        for contract in output["contracts"]
    )


def test_contract_validation_includes_model_acquisition_path_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert any(
        result["name"] == "model-acquisition-path"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in output["results"]
    )


def test_evidence_chain_places_model_acquisition_path_after_runtime_tool_availability(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)
    steps = [item["step"] for item in output["chain"]]

    runtime_index = steps.index("runtime-tool-availability")
    path_index = steps.index("model-acquisition-path")

    assert path_index == runtime_index + 1
