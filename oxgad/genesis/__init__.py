"""OriginX Legendary Genesis production domain."""

from oxgad.genesis.identity import (
    GENESIS_BATCH_ID,
    GENESIS_GENERATION_VERSION,
    GENESIS_IDENTITY_VERSION,
    GENESIS_MAXIMUM_SUPPLY,
    build_genesis_batch_identities,
    build_genesis_identity,
    validate_genesis_identity,
)

__all__ = (
    "GENESIS_BATCH_ID",
    "GENESIS_GENERATION_VERSION",
    "GENESIS_IDENTITY_VERSION",
    "GENESIS_MAXIMUM_SUPPLY",
    "build_genesis_batch_identities",
    "build_genesis_identity",
    "validate_genesis_identity",
)
