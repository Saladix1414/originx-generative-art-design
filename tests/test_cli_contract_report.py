import json

from oxgad.cli import main


def test_cli_contract_report_lists_known_contracts(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["count"] >= 13

    names = {
        contract["name"]
        for contract in output["contracts"]
    }

    assert {
        "provenance",
        "quality",
        "promotion",
        "ledger",
        "output",
        "review",
        "release",
        "export-result",
        "project-readiness",
    }.issubset(names)


def test_cli_contract_report_uses_local_schema_paths(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    for contract in output["contracts"]:
        assert contract["path"].startswith("schemas/")
        assert contract["path"].endswith(".schema.json")
        assert contract["schema_id"].endswith(".schema.json")
