from __future__ import annotations

from typing import Any

from oxgad.master_prompt.gates import evaluate_master_prompt_gates


def _score_boolean(value: bool) -> int:
    return 100 if value else 0


def _text_score(value: str, minimum_length: int) -> int:
    if not value:
        return 0

    return 100 if len(value.strip()) >= minimum_length else 50


def evaluate_master_prompt_quality(
    master_prompt: dict[str, Any],
) -> dict[str, Any]:
    prompt = master_prompt.get("prompt", {})
    detail = master_prompt.get("detail_priorities", {})
    controlled = master_prompt.get("controlled_vocabulary", {})
    gates = evaluate_master_prompt_gates(master_prompt)

    positive_score = _text_score(str(prompt.get("positive", "")), 40)
    negative_score = _text_score(str(prompt.get("negative", "")), 40)
    macro_score = _score_boolean(bool(detail.get("macro")))
    meso_score = _score_boolean(bool(detail.get("meso")))
    micro_score = _score_boolean(bool(detail.get("micro")))
    trait_score = _score_boolean(bool(controlled.get("trait_families")))
    safety_score = _score_boolean(gates["safety_complete"])
    gate_score = _score_boolean(gates["passed"])

    scores = {
        "positive_prompt_score": positive_score,
        "negative_prompt_score": negative_score,
        "macro_detail_score": macro_score,
        "meso_detail_score": meso_score,
        "micro_detail_score": micro_score,
        "trait_coverage_score": trait_score,
        "safety_score": safety_score,
        "gate_score": gate_score,
    }

    total = sum(scores.values())
    average = total // len(scores)

    return {
        "passed": average >= 80 and gates["passed"],
        "score": average,
        "scores": scores,
        "gates": gates,
    }
