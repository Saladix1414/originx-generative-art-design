import json

from oxgad.cli import main


def test_cli_schema_prints_identity_fields(tmp_path, capsys):
    payload = {
        "schema_version": "ox-project-readiness-summary-1",
        "project": "originx-generative-art-design",
        "phase": "phase20",
        "status": "ready",
    }
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["schema", str(path)]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output == {
        "schema_version": "ox-project-readiness-summary-1",
        "project": "originx-generative-art-design",
        "phase": "phase20",
    }


def test_cli_status_prints_status_and_decision_fields(tmp_path, capsys):
    payload = {
        "schema_version": "ox-canonical-promotion-1",
        "project": "originx-generative-art-design",
        "phase": "phase10",
        "decision": "promoted",
    }
    path = tmp_path / "promotion.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["status", str(path)]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output == {
        "status": None,
        "decision": "promoted",
        "phase": "phase10",
    }
