import copy
import json
from pathlib import Path

from oxgad.master_prompt import evaluate_master_prompt_quality


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")


def _prompt():
    return json.loads(FIXTURE.read_text())


def test_master_prompt_quality_passes_fixture():
    quality = evaluate_master_prompt_quality(_prompt())

    assert quality["passed"] is True
    assert quality["score"] >= 80
    assert quality["gates"]["passed"] is True


def test_master_prompt_quality_reports_scores():
    quality = evaluate_master_prompt_quality(_prompt())

    assert set(quality["scores"]) == {
        "positive_prompt_score",
        "negative_prompt_score",
        "macro_detail_score",
        "meso_detail_score",
        "micro_detail_score",
        "trait_coverage_score",
        "safety_score",
        "gate_score",
    }


def test_master_prompt_quality_fails_blocked_prompt():
    prompt = _prompt()
    prompt["prompt"]["positive"] += " https://example.com"

    quality = evaluate_master_prompt_quality(prompt)

    assert quality["passed"] is False
    assert quality["gates"]["blocked_terms"] == ["https://"]


def test_master_prompt_quality_fails_missing_micro_detail():
    prompt = copy.deepcopy(_prompt())
    prompt["detail_priorities"]["micro"] = []

    quality = evaluate_master_prompt_quality(prompt)

    assert quality["passed"] is False
    assert quality["scores"]["micro_detail_score"] == 0
    assert quality["gates"]["detail_complete"] is False
