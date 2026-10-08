import json
from pathlib import Path

from oxgad.cli import main


def test_cli_validate_fixture_accepts_project_readiness_fixture(capsys):
    assert (
        main(
            [
                "validate-fixture",
                "tests/fixtures/cli/project-readiness-summary.json",
                "--schema",
                "schemas/ox-project-readiness-summary-1.schema.json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)

    assert output == {
        "valid": True,
        "schema_version": "ox-project-readiness-summary-1",
        "schema_id": "ox-project-readiness-summary-1.schema.json",
    }


def test_cli_validate_fixture_accepts_promotion_fixture(capsys):
    assert (
        main(
            [
                "validate-fixture",
                "tests/fixtures/cli/canonical-promotion.json",
                "--schema",
                "schemas/ox-canonical-promotion-1.schema.json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert output["schema_version"] == "ox-canonical-promotion-1"
    assert output["schema_id"] == "ox-canonical-promotion-1.schema.json"
