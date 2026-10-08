import json
from pathlib import Path

from oxgad.cli import main


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")


def test_prompt_chain_reports_schema_valid(capsys):
    assert main(["prompt-chain", str(FIXTURE)]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["valid"] is True
    assert output["schema_valid"] is True
    assert output["chainVersion"] == "OX-MASTER-PROMPT-EVIDENCE-CHAIN-1"


def test_prompt_chain_schema_validation_rejects_hash_mismatch(
    tmp_path,
    capsys,
):
    payload = json.loads(
        FIXTURE.read_text()
    )
    payload["render_binding"]["master_prompt_hash"] = "0" * 64

    path = tmp_path / "bad-prompt.json"
    path.write_text(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )

    assert main(["prompt-chain", str(path)]) == 2

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["valid"] is False
    assert "Master prompt hash mismatch" in output["error"]
