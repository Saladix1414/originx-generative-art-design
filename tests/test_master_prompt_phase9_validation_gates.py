import copy
import json
from pathlib import Path

from oxgad.master_prompt import evaluate_master_prompt_gates


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")


def _prompt():
    return json.loads(FIXTURE.read_text())


def test_master_prompt_gates_pass_fixture():
    result = evaluate_master_prompt_gates(_prompt())

    assert result == {
        "passed": True,
        "blocked_terms": [],
        "missing_negative_terms": [],
        "detail_complete": True,
        "safety_complete": True,
    }


def test_master_prompt_gates_detect_blocked_terms():
    prompt = _prompt()
    prompt["prompt"]["positive"] += " https://example.com celebrity"

    result = evaluate_master_prompt_gates(prompt)

    assert result["passed"] is False
    assert "https://" in result["blocked_terms"]
    assert "celebrity" in result["blocked_terms"]


def test_master_prompt_gates_detect_missing_negative_terms():
    prompt = _prompt()
    prompt["prompt"]["negative"] = "watermark"

    result = evaluate_master_prompt_gates(prompt)

    assert result["passed"] is False
    assert "broken anatomy" in result["missing_negative_terms"]


def test_master_prompt_gates_detect_missing_detail():
    prompt = copy.deepcopy(_prompt())
    prompt["detail_priorities"]["micro"] = []

    result = evaluate_master_prompt_gates(prompt)

    assert result["passed"] is False
    assert result["detail_complete"] is False


def test_master_prompt_gates_detect_safety_violation():
    prompt = _prompt()
    prompt["safety_boundaries"]["no_network"] = False

    result = evaluate_master_prompt_gates(prompt)

    assert result["passed"] is False
    assert result["safety_complete"] is False
