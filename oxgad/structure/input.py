"""OX-GAD PHASE 2B — public Structure Engine input contract."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from oxgad.structure.canonical import (
    CanonicalizationError,
    canonical_json,
)


SUPPORTED_TIERS = frozenset(
    {
        "RARE",
        "EPIC",
        "LEGENDARY",
    }
)

SERIAL_PATTERN = re.compile(
    r"^#[0-9]{4,6}$"
)

HASH_PATTERN = re.compile(
    r"^sha256:[0-9a-f]{64}$"
)

ALLOWED_INPUT_FIELDS = frozenset(
    {
        "tokenId",
        "serial",
        "canonicalName",
        "tier",
        "generationTheme",
        "dna",
        "dnaHash",
        "resonance",
        "seed",
    }
)

REQUIRED_INPUT_FIELDS = frozenset(
    {
        "tokenId",
        "serial",
        "canonicalName",
        "tier",
        "generationTheme",
        "dna",
        "dnaHash",
        "resonance",
    }
)


class StructureInputError(ValueError):
    """Raised when an Identity Input package is invalid."""


def _non_empty_string(
    value: Any,
    field: str,
) -> str:
    if not isinstance(value, str):
        raise StructureInputError(
            f"{field} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise StructureInputError(
            f"{field} must not be empty."
        )

    return normalized


def _canonical_copy(
    value: Any,
    field: str,
) -> Any:
    try:
        serialized = canonical_json(
            value
        )
    except CanonicalizationError as exc:
        raise StructureInputError(
            f"{field} is not canonicalizable: {exc}"
        ) from exc

    return json.loads(
        serialized
    )


@dataclass(
    frozen=True,
    slots=True,
)
class StructureInput:
    """Validated public input for OriginX Structure Engine."""

    token_id: int
    serial: str
    canonical_name: str
    tier: str
    generation_theme: str
    dna: Mapping[str, Any]
    dna_hash: str
    resonance: Mapping[str, Any]
    explicit_seed: int | None = None

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
    ) -> StructureInput:
        if not isinstance(value, Mapping):
            raise StructureInputError(
                "Structure Input must be an object."
            )

        supplied = set(
            value.keys()
        )

        if not all(
            isinstance(key, str)
            for key in supplied
        ):
            raise StructureInputError(
                "Structure Input keys must be strings."
            )

        unexpected = sorted(
            supplied
            - ALLOWED_INPUT_FIELDS
        )

        if unexpected:
            raise StructureInputError(
                "Unexpected Structure Input fields: "
                + ", ".join(unexpected)
            )

        missing = sorted(
            REQUIRED_INPUT_FIELDS
            - supplied
        )

        if missing:
            raise StructureInputError(
                "Missing Structure Input fields: "
                + ", ".join(missing)
            )

        token_id = value["tokenId"]

        if (
            not isinstance(token_id, int)
            or isinstance(token_id, bool)
            or token_id < 1
        ):
            raise StructureInputError(
                "tokenId must be an integer >= 1."
            )

        serial = _non_empty_string(
            value["serial"],
            "serial",
        )

        if SERIAL_PATTERN.fullmatch(
            serial
        ) is None:
            raise StructureInputError(
                "serial must match # followed by "
                "4 to 6 digits."
            )

        canonical_name = _non_empty_string(
            value["canonicalName"],
            "canonicalName",
        )

        tier = _non_empty_string(
            value["tier"],
            "tier",
        )

        if tier not in SUPPORTED_TIERS:
            raise StructureInputError(
                "Unsupported tier: "
                f"{tier!r}."
            )

        generation_theme = _non_empty_string(
            value["generationTheme"],
            "generationTheme",
        )

        dna = value["dna"]

        if (
            not isinstance(dna, Mapping)
            or not dna
        ):
            raise StructureInputError(
                "dna must be a non-empty object."
            )

        normalized_dna = _canonical_copy(
            dna,
            "dna",
        )

        if not isinstance(
            normalized_dna,
            dict,
        ):
            raise StructureInputError(
                "dna must canonicalize to an object."
            )

        dna_hash = _non_empty_string(
            value["dnaHash"],
            "dnaHash",
        )

        if HASH_PATTERN.fullmatch(
            dna_hash
        ) is None:
            raise StructureInputError(
                "dnaHash must be a canonical "
                "sha256:<64 lowercase hex> digest."
            )

        resonance = value[
            "resonance"
        ]

        if not isinstance(
            resonance,
            Mapping,
        ):
            raise StructureInputError(
                "resonance must be an object."
            )

        normalized_resonance = (
            _canonical_copy(
                resonance,
                "resonance",
            )
        )

        if not isinstance(
            normalized_resonance,
            dict,
        ):
            raise StructureInputError(
                "resonance must canonicalize "
                "to an object."
            )

        explicit_seed = value.get(
            "seed"
        )

        if explicit_seed is not None:
            if (
                not isinstance(
                    explicit_seed,
                    int,
                )
                or isinstance(
                    explicit_seed,
                    bool,
                )
                or explicit_seed < 0
                or explicit_seed
                > 18_446_744_073_709_551_615
            ):
                raise StructureInputError(
                    "seed must be an unsigned "
                    "64-bit integer."
                )

        return cls(
            token_id=token_id,
            serial=serial,
            canonical_name=canonical_name,
            tier=tier,
            generation_theme=generation_theme,
            dna=normalized_dna,
            dna_hash=dna_hash,
            resonance=normalized_resonance,
            explicit_seed=explicit_seed,
        )

    def seed_material(
        self,
    ) -> dict[str, Any]:
        """Return stable public material used for seed derivation."""

        return {
            "tokenId": self.token_id,
            "serial": self.serial,
            "canonicalName": self.canonical_name,
            "tier": self.tier,
            "generationTheme": self.generation_theme,
            "dnaHash": self.dna_hash,
            "resonance": self.resonance,
        }
