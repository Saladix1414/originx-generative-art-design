import json
import re

from oxgad.cli import main


def test_prompt_inspect_reports_master_prompt_summary(capsys):
    assert main(["prompt-inspect", "tests/fixtures/master-prompt/candidate.json"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["schema_version"] == "ox-master-prompt-1"
    assert output["prompt_id"] == "master-prompt-token-0001-candidate"
    assert output["render_intent"] == "candidate"
    assert output["composition_profile"]
    assert output["trait_family_count"] > 0
    assert output["positive_length"] > 0
    assert output["negative_length"] > 0
    assert re.fullmatch(r"[a-f0-9]{64}", output["master_prompt_hash"])


def test_prompt_inspect_is_deterministic(capsys):
    assert main(["prompt-inspect", "tests/fixtures/master-prompt/candidate.json"]) == 0
    first = json.loads(capsys.readouterr().out)

    assert main(["prompt-inspect", "tests/fixtures/master-prompt/candidate.json"]) == 0
    second = json.loads(capsys.readouterr().out)

    assert first == second
