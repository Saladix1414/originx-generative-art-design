from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT),
)

from oxgad.render.dragon_prompt_compiler import (
    compile_negative_prompt,
    compile_positive_prompt,
)
from oxgad.structure.dragon_identity_rules import (
    RULE_VERSION,
    validate_coherence,
)


def main() -> None:
    files = [
        ROOT
        / "schemas"
        / "ox-dragon-identity-1.schema.json",

        ROOT
        / "config"
        / "dragon_identity_catalogs_v1.json",

        ROOT
        / "specs"
        / "examples"
        / "legendary-dragon-example.json",
    ]

    for path in files:
        json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    example = json.loads(
        (
            ROOT
            / "specs"
            / "examples"
            / "legendary-dragon-example.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert (
        example["identity"]["tier"]
        == "LEGENDARY"
    )

    assert (
        example["identity"]["cohort"]
        == "GENESIS"
    )

    assert (
        example["qualityTarget"]["minimumScore"]
        == 92
    )

    errors = validate_coherence(
        example
    )

    assert not errors, errors

    prompt = compile_positive_prompt(
        example
    )

    negative = compile_negative_prompt()

    assert "Vaerkaion" in prompt
    assert "abyssal flame" in prompt
    assert "generic dragon" in negative

    assert RULE_VERSION == "OX-DRAGON-RULES-1"

    print(
        "OX_DRAGON_IDENTITY_JSON=PASS"
    )

    print(
        "OX_DRAGON_COHERENCE=PASS"
    )

    print(
        "OX_DRAGON_PROMPT_COMPILER=PASS"
    )

    print(
        "OX_DRAGON_NEGATIVE_PROMPT=PASS"
    )

    print(
        "OX_DRAGON_IDENTITY_SYSTEM=PASS"
    )


if __name__ == "__main__":
    main()
