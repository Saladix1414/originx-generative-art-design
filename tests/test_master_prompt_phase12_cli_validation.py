import json
from pathlib import Path

from oxgad.cli import main


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")


def test_prompt_validate_accepts_valid_fixture(capsys):
    assert main(["prompt-validate", str(FIXTURE)]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is True
    assert output["schema_valid"] is True
    assert output["quality_passed"] is True
    assert output["score"] >= 80
    assert len(output["master_prompt_hash"]) == 64
    assert output["gates"]["passed"] is True


def test_prompt_validate_rejects_schema_invalid_payload(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "ox-master-prompt-1",
                "project": "originx-generative-art-design",
            }
        )
    )

    assert main(["prompt-validate", str(path)]) == 2

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is False
    assert output["schema_valid"] is False
    assert output["quality_passed"] is False
    assert output["error"]


def test_prompt_validate_rejects_blocked_positive_language(tmp_path, capsys):
    payload = json.loads(FIXTURE.read_text())
    payload["prompt"]["positive"] = (
        payload["prompt"]["positive"]
        + " https://example.invalid"
    )

    path = tmp_path / "blocked.json"
    path.write_text(json.dumps(payload, sort_keys=True))

    assert main(["prompt-validate", str(path)]) == 2

    output = json.loads(capsys.readouterr().out)

    assert output["valid"] is False
    assert output["schema_valid"] is True
    assert output["quality_passed"] is False
    assert "https://" in output["gates"]["blocked_terms"]
