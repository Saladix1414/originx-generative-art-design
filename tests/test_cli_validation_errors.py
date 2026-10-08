import json

from oxgad.cli import main


def test_cli_validate_fixture_returns_json_error_for_invalid_payload(tmp_path, capsys):
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "schema_version": "ox-project-readiness-summary-1",
                "project": "originx-generative-art-design",
                "phase": "phase20",
                "status": "wrong",
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

    result = main(
        [
            "validate-fixture",
            str(invalid),
            "--schema",
            "schemas/ox-project-readiness-summary-1.schema.json",
        ]
    )

    output = json.loads(capsys.readouterr().out)

    assert result == 2
    assert output["valid"] is False
    assert output["schema_version"] == "ox-project-readiness-summary-1"
    assert output["schema_id"] == "ox-project-readiness-summary-1.schema.json"
    assert "wrong" in output["error"]


def test_cli_validate_fixture_still_returns_zero_for_valid_payload(capsys):
    result = main(
        [
            "validate-fixture",
            "tests/fixtures/cli/project-readiness-summary.json",
            "--schema",
            "schemas/ox-project-readiness-summary-1.schema.json",
        ]
    )

    output = json.loads(capsys.readouterr().out)

    assert result == 0
    assert output["valid"] is True
