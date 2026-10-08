"""OX-GAD PHASE 2F — public OriginX Structure Engine API."""

from oxgad.structure.assembler import (
    STRUCTURE_ASSEMBLER_VERSION,
    ArtSpecAssembly,
    ArtSpecAssemblyError,
    assemble_art_spec,
)
from oxgad.structure.deterministic import (
    STRUCTURE_DETERMINISM_VERSION,
    DeterministicSelectionError,
    derive_seed,
    deterministic_choice,
    deterministic_index,
    resolve_seed,
)
from oxgad.structure.input import (
    StructureInput,
    StructureInputError,
)
from oxgad.structure.rules import (
    STRUCTURE_RULESET_VERSION,
    StructureRuleError,
    era_for_tier,
    tier_rule,
)


__all__ = (
    "STRUCTURE_ASSEMBLER_VERSION",
    "STRUCTURE_DETERMINISM_VERSION",
    "STRUCTURE_RULESET_VERSION",
    "ArtSpecAssembly",
    "ArtSpecAssemblyError",
    "DeterministicSelectionError",
    "StructureInput",
    "StructureInputError",
    "StructureRuleError",
    "assemble_art_spec",
    "derive_seed",
    "deterministic_choice",
    "deterministic_index",
    "era_for_tier",
    "resolve_seed",
    "tier_rule",
)
