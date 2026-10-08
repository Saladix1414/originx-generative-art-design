<!-- OX-GAD PHASE 3E -->

# OriginX Art Design Grammar — Phase 3 Closure

## Status

PHASE 3 — Art Design Grammar is complete.

The phase establishes the formal visual grammar that governs how OriginX identities evolve from Primitive Origin through Evolved Origin to Ascended Origin.

The grammar remains structured, deterministic, provider-independent and separate from rendering.

## Canonical design pipeline

```text
tier + deterministic seed
  ↓
Art Rule Catalog
  ↓
Formal Art Design Grammar
  ↓
Integrated Design Contract
  ↓
designHash
  ↓
Structure Engine
  ↓
OX-ART-SPEC-1
```

## Canonical versions

- OX-ART-RULES-1
- OX-ART-GRAMMAR-1
- OX-ART-DESIGN-INTEGRATION-1
- OX-STRUCTURE-ASSEMBLER-1
- OX-ART-SPEC-1

## Grammar domains

- morphology
- anatomy
- materials
- technology
- augmentation
- architecture
- lighting
- atmosphere
- weathering
- ornament
- damage

## Detail authority

```text
MACRO > MESO > MICRO
```

Anatomy, silhouette, physical mass, pose and composition retain authority over secondary or microscopic detail.

Microdetail must never conceal incorrect anatomy.

## Tier evolution

```text
RARE       → Primitive Origin
EPIC       → Evolved Origin
LEGENDARY  → Ascended Origin
```

Evolution is structural rather than a simple increase in brightness, ornament or visual noise.

Technology, morphology and augmentation may increase with evolution while weathering and damage may decrease.

This prevents higher tiers from becoming visually saturated merely because they are rarer.

## Art Rule Catalog

The Art Rule Catalog provides deterministic tier-specific visual selections such as body mass, silhouette, armor, technology, architecture, materials, lighting, atmosphere, camera and composition.

Its existing `artRuleHash` remains canonical and retains its original meaning.

## Formal Art Grammar

The Formal Art Grammar defines tier-level structural laws and visual invariants.

It does not generate prompts, invoke models or select providers.

## Integrated Design Contract

The Integrated Design Contract binds the deterministic Art Rule Catalog output to the Formal Art Grammar.

It verifies agreement for:

- tier
- era
- evolution rank
- detail authority
- provider independence
- render independence

The integrated payload receives a canonical `designHash`.

## Hash boundaries

```text
artRuleHash  = deterministic Art Rule Catalog evidence
designHash   = deterministic integrated design evidence
artSpecHash  = deterministic OX-ART-SPEC-1 evidence
```

These hashes have distinct meanings and must not be substituted for one another.

## Structure Engine integration

`ArtSpecAssembly` now exposes external evidence:

```text
art_spec
art_spec_hash
art_rule_hash
design_hash
seed
```

`design_hash` remains outside `OX-ART-SPEC-1`.

The Art Spec schema remains closed with `additionalProperties: false`.

PHASE 3 did not modify the OX-ART-SPEC-1 schema.

## Historical preservation

The first ten PHASE 2 Art Specs remain unchanged.

Their historical `artSpecHash` values and PHASE 2E manifest remain preserved.

PHASE 3 therefore adds design evidence without rewriting previous canonical structural output.

## Governance

```text
AI OUTPUT != CANONICAL ART
CANDIDATE != APPROVED ART
HIGH DETAIL != HIGH QUALITY
QUALITY SCORE != FINAL AUTHORITY
EXTERNAL PROVIDER != CANONICAL DEPENDENCY
```

Canonical artwork approval remains manual.

## Explicit non-goals

PHASE 3 does not implement:

- prompt compilation
- positive or negative diffusion prompts
- image generation
- model loading
- LoRA execution
- ControlNet execution
- GPU inference
- provider execution
- canonical artwork approval

## Next stage

```text
PHASE 4 — OriginX Render Compiler
```

PHASE 4 may consume structured design authority, but rendering must remain downstream from canonical design truth.
