import json

from oxgad.cli import main


def test_cli_validate_fixtures_accepts_fixture_directory(capsys):
    assert main(["validate-fixtures", "tests/fixtures/cli"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert output["count"] == 2

    names = {
        result["path"].split("/")[-1]
        for result in output["results"]
    }

    assert names == {
        "canonical-promotion.json",
        "project-readiness-summary.json",
    }


def test_cli_validate_fixtures_blocks_unmapped_json(tmp_path, capsys):
    fixture = tmp_path / "unknown.json"
    fixture.write_text("{}", encoding="utf-8")

    assert main(["validate-fixtures", str(tmp_path)]) == 2

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is False
    assert output["count"] == 1
    assert output["results"][0]["error"] == "no schema mapping"
