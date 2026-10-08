import json


from oxgad.cli import main


def test_validate_fixture_error_output_is_json(tmp_path, capsys):
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "schema_version": "ox-project-readiness-summary-1",
                "project": "originx-generative-art-design",
                "phase": "phase20",
                "status": "invalid",
                "checks": {
                    "review_ready": True,
                    "release_ready": True,
                    "release_recorded": True,
                    "export_recorded": True,
                },
            }
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                "validate-fixture",
                str(invalid),
                "--schema",
                "schemas/ox-project-readiness-summary-1.schema.json",
            ]
        )
        == 2
    )

    captured = capsys.readouterr()

    output = json.loads(captured.out)

    assert captured.err == ""
    assert output["valid"] is False
    assert output["schema_version"] == "ox-project-readiness-summary-1"
    assert output["schema_id"] == "ox-project-readiness-summary-1.schema.json"
    assert "error" in output


def test_validate_fixtures_error_output_is_json(tmp_path, capsys):
    unknown = tmp_path / "unknown.json"
    unknown.write_text("{}", encoding="utf-8")

    assert main(["validate-fixtures", str(tmp_path)]) == 2

    captured = capsys.readouterr()

    output = json.loads(captured.out)

    assert captured.err == ""
    assert output["valid"] is False
    assert output["count"] == 1
    assert output["results"][0]["error"] == "no schema mapping"


def test_readiness_error_output_is_json(tmp_path, capsys):
    unknown = tmp_path / "unknown.json"
    unknown.write_text("{}", encoding="utf-8")

    assert main(["readiness", "--fixtures", str(tmp_path)]) == 2

    captured = capsys.readouterr()

    output = json.loads(captured.out)

    assert captured.err == ""
    assert output["ready"] is False
    assert output["fixtures_valid"] is False
    assert output["contracts_valid"] is True
