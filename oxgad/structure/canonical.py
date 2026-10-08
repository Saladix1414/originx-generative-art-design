"""Canonical serialization and hashing for OX-ART-SPEC-1."""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any

from oxgad import ART_SPEC_VERSION


CANONICAL_SERIALIZATION_VERSION = "OX-CANONICAL-JSON-1"
HASH_ALGORITHM = "sha256"


class CanonicalizationError(ValueError):
    """Raised when canonical serialization cannot be performed."""


def _normalize_string(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _normalize_json(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalizationError(
                "NaN and infinite numbers are forbidden"
            )
        return 0.0 if value == 0.0 else value

    if isinstance(value, str):
        return _normalize_string(value)

    if isinstance(value, Mapping):
        result: dict[str, Any] = {}

        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(
                    "Canonical object keys must be strings"
                )

            normalized_key = _normalize_string(key)

            if normalized_key in result:
                raise CanonicalizationError(
                    "Unicode normalization produced duplicate keys"
                )

            result[normalized_key] = _normalize_json(item)

        return result

    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [_normalize_json(item) for item in value]

    raise CanonicalizationError(
        f"Unsupported canonical value type: {type(value).__name__}"
    )


def canonical_json(value: Any) -> str:
    return json.dumps(
        _normalize_json(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    digest = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return f"{HASH_ALGORITHM}:{digest}"


def art_spec_hash(art_spec: Mapping[str, Any]) -> str:
    version = art_spec.get("specVersion")

    if version != ART_SPEC_VERSION:
        raise CanonicalizationError(
            f"Unsupported Art Spec version: {version!r}"
        )

    return canonical_sha256(art_spec)
