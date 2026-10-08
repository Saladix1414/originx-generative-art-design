import importlib.metadata
import json

from oxgad.cli import main


def test_installed_distribution_exposes_metadata():
    metadata = importlib.metadata.metadata("originx-generative-art-design")

    assert metadata["Name"] == "originx-generative-art-design"


def test_installed_console_script_contract(tmp_path, capsys):
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

    assert output["schema_version"] == "ox-project-readiness-summary-1"
    assert output["project"] == "originx-generative-art-design"
    assert output["phase"] == "phase20"
