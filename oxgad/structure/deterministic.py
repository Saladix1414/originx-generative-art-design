"""OX-GAD PHASE 2B — deterministic Structure Engine primitives."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import TypeVar

from oxgad.structure.canonical import (
    canonical_bytes,
)
from oxgad.structure.input import (
    StructureInput,
)


STRUCTURE_DETERMINISM_VERSION = (
    "OX-STRUCTURE-DETERMINISM-1"
)

UINT64_MAX = (
    18_446_744_073_709_551_615
)

T = TypeVar("T")


class DeterministicSelectionError(
    ValueError
):
    """Raised when deterministic selection input is invalid."""


def _digest(
    *,
    seed: int,
    namespace: str,
) -> bytes:
    if (
        not isinstance(seed, int)
        or isinstance(seed, bool)
        or seed < 0
        or seed > UINT64_MAX
    ):
        raise DeterministicSelectionError(
            "seed must be an unsigned 64-bit integer."
        )

    if (
        not isinstance(namespace, str)
        or not namespace.strip()
    ):
        raise DeterministicSelectionError(
            "namespace must be a non-empty string."
        )

    material = {
        "version": STRUCTURE_DETERMINISM_VERSION,
        "seed": seed,
        "namespace": namespace.strip(),
    }

    return hashlib.sha256(
        canonical_bytes(
            material
        )
    ).digest()


def derive_seed(
    structure_input: StructureInput,
) -> int:
    """Derive a stable unsigned 64-bit seed."""

    material = {
        "version": STRUCTURE_DETERMINISM_VERSION,
        "input": structure_input.seed_material(),
    }

    digest = hashlib.sha256(
        canonical_bytes(
            material
        )
    ).digest()

    return int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )


def resolve_seed(
    structure_input: StructureInput,
) -> int:
    """Use explicit seed when supplied, otherwise derive one."""

    if (
        structure_input.explicit_seed
        is not None
    ):
        return structure_input.explicit_seed

    return derive_seed(
        structure_input
    )


def deterministic_index(
    *,
    seed: int,
    namespace: str,
    size: int,
) -> int:
    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
    ):
        raise DeterministicSelectionError(
            "size must be an integer > 0."
        )

    digest = _digest(
        seed=seed,
        namespace=namespace,
    )

    value = int.from_bytes(
        digest,
        byteorder="big",
        signed=False,
    )

    return value % size


def deterministic_choice(
    options: Sequence[T],
    *,
    seed: int,
    namespace: str,
) -> T:
    if not options:
        raise DeterministicSelectionError(
            "options must not be empty."
        )

    index = deterministic_index(
        seed=seed,
        namespace=namespace,
        size=len(options),
    )

    return options[index]
