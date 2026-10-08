from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


def canonical_master_prompt_json(
    master_prompt: Mapping[str, Any],
) -> str:
    return json.dumps(
        master_prompt,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def master_prompt_hash(
    master_prompt: Mapping[str, Any],
) -> str:
    return sha256(
        canonical_master_prompt_json(master_prompt).encode("utf-8")
    ).hexdigest()
