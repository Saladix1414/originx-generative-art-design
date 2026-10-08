import json
from pathlib import Path

from oxgad.cli import main


FIXTURE_DIR = Path("tests/fixtures/cli")


def test_cli_schema_reads_project_readiness_fixture(capsys):
    assert main(["schema", str(FIXTURE_DIR / "project-readiness-summary.json")]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output == {
        "schema_version": "ox-project-readiness-summary-1",
        "project": "originx-generative-art-design",
        "phase": "phase20",
    }


def test_cli_status_reads_project_readiness_fixture(capsys):
    assert main(["status", str(FIXTURE_DIR / "project-readiness-summary.json")]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["status"] == "ready"
    assert output["decision"] is None
    assert output["phase"] == "phase20"


def test_cli_status_reads_promotion_fixture(capsys):
    assert main(["status", str(FIXTURE_DIR / "canonical-promotion.json")]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["status"] is None
    assert output["decision"] == "promoted"
    assert output["phase"] == "phase10"


def test_cli_fixtures_are_small_and_local():
    for path in FIXTURE_DIR.glob("*.json"):
        text = path.read_text()

        assert path.stat().st_size < 4096
        assert "http://" not in text
        assert "https://" not in text
        assert "PRIVATE_KEY" not in text
