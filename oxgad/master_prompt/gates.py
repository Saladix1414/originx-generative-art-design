from __future__ import annotations

from typing import Any


BLOCKED_TEXT = (
    "http://",
    "https://",
    "api key",
    "private_key",
    "secret",
    "token=",
    "celebrity",
    "trademark",
    "franchise",
    "download",
    "upload",
)

REQUIRED_NEGATIVE_TERMS = (
    "watermark",
    "text artifacts",
    "logo",
    "extra limbs",
    "broken anatomy",
)


def _positive_prompt_text(master_prompt: dict[str, Any]) -> str:
    prompt = master_prompt.get("prompt", {})

    return str(prompt.get("positive", "")).lower()


def evaluate_master_prompt_gates(
    master_prompt: dict[str, Any],
) -> dict[str, Any]:
    positive = _positive_prompt_text(master_prompt)
    negative = str(master_prompt.get("prompt", {}).get("negative", "")).lower()
    detail = master_prompt.get("detail_priorities", {})

    blocked_terms = [
        term
        for term in BLOCKED_TEXT
        if term in positive
    ]

    missing_negative_terms = [
        term
        for term in REQUIRED_NEGATIVE_TERMS
        if term not in negative
    ]

    detail_complete = all(
        isinstance(detail.get(key), list) and len(detail[key]) > 0
        for key in ("macro", "meso", "micro")
    )

    safety = master_prompt.get("safety_boundaries", {})
    safety_complete = all(
        safety.get(key) is True
        for key in (
            "local_first",
            "no_network",
            "no_external_provider_dependency",
            "no_uncontrolled_text",
            "no_franchise_style",
        )
    )

    passed = (
        not blocked_terms
        and not missing_negative_terms
        and detail_complete
        and safety_complete
    )

    return {
        "passed": passed,
        "blocked_terms": blocked_terms,
        "missing_negative_terms": missing_negative_terms,
        "detail_complete": detail_complete,
        "safety_complete": safety_complete,
    }
