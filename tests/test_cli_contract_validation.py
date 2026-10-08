import json

from oxgad.cli import main


def test_cli_validate_contracts_accepts_registered_schemas(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert output["count"] >= 13

    for result in output["results"]:
        assert result["valid"] is True
        assert result["path"].startswith("schemas/")
        assert result["schema_id"].endswith(".schema.json")


def test_cli_validate_contracts_includes_project_readiness(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(capsys.readouterr().out)

    names = {
        result["name"]
        for result in output["results"]
    }

    assert "project-readiness" in names
