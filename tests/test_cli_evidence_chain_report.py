import json

from oxgad.cli import main


def test_cli_evidence_chain_reports_expected_order(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["count"] == 13

    steps = [
        item["step"]
        for item in output["chain"]
    ]

    assert steps == [
        "provenance",
        "quality",
        "promotion",
        "canonical-ledger",
        "canonical-output",
        "review",
        "release-readiness",
        "release-ledger",
        "export-plan",
        "export-dry-run",
        "export-result",
        "export-audit",
        "project-readiness",
    ]


def test_cli_evidence_chain_schemas_are_registered_contracts(capsys):
    assert main(["contracts"]) == 0
    contracts = json.loads(capsys.readouterr().out)

    contract_schema_ids = {
        contract["schema_id"]
        for contract in contracts["contracts"]
    }

    assert main(["evidence-chain"]) == 0
    chain = json.loads(capsys.readouterr().out)

    for item in chain["chain"]:
        assert item["schema"] in contract_schema_ids
