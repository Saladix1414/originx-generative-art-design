import json

from oxgad.cli import main


SCHEMA_PATH = "schemas/ox-runtime-tool-availability-1.schema.json"


def test_contract_registry_lists_runtime_tool_availability_schema(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert any(
        contract["name"] == "runtime-tool-availability"
        and contract["path"] == SCHEMA_PATH
        and contract["schema_id"] == "ox-runtime-tool-availability-1.schema.json"
        for contract in output["contracts"]
    )


def test_contract_validation_includes_runtime_tool_availability_schema(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert any(
        result["name"] == "runtime-tool-availability"
        and result["path"] == SCHEMA_PATH
        and result["valid"] is True
        for result in output["results"]
    )


def test_evidence_chain_places_runtime_tool_after_placement_verification(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)
    steps = [item["step"] for item in output["chain"]]

    assert steps.index("model-artifact-placement-verification") < steps.index(
        "runtime-tool-availability"
    )
