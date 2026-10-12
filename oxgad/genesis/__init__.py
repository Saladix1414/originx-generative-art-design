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
from oxgad.genesis.lore import (
    AKASHIC_VERSION,
    GENESIS_LORE_VERSION,
    GLYPH_VERSION,
    RESONANCE_VERSION,
    build_genesis_batch_lore,
    build_genesis_lore,
    build_glyph,
    build_initial_akashic,
    build_resonance,
    validate_genesis_lore,
    verify_akashic_chain,
)

__all__ = (
    "AKASHIC_VERSION",
    "GENESIS_BATCH_ID",
    "GENESIS_GENERATION_VERSION",
    "GENESIS_IDENTITY_VERSION",
    "GENESIS_LORE_VERSION",
    "GENESIS_MAXIMUM_SUPPLY",
    "GLYPH_VERSION",
    "RESONANCE_VERSION",
    "build_genesis_batch_identities",
    "build_genesis_batch_lore",
    "build_genesis_identity",
    "build_genesis_lore",
    "build_glyph",
    "build_initial_akashic",
    "build_resonance",
    "validate_genesis_identity",
    "validate_genesis_lore",
    "verify_akashic_chain",
)
