# OriginX Generative Art Design — Architecture v1

Status: FOUNDATION

## Project boundary

OriginX Generative Art Design owns the generative-art pipeline.

It does not own:

- payments
- membership state
- blockchain ownership
- NFT mint authority
- customer identity
- access entitlement

## Core pipeline

Identity Contract
→ Art Design
→ Structure Engine
→ OX-ART-SPEC
→ OriginX Render
→ OX-RENDER
→ Local Forge
→ Detail Engine
→ Quality Engine
→ Canonicalization
→ Provenance

## Local-first

OriginX Local Forge is the preferred execution layer.

External image providers are optional adapters only.

## Detail hierarchy

### Macro

- anatomy
- silhouette
- pose
- camera
- composition
- environment

### Meso

- scales
- armor
- horns
- wings
- architecture
- mechanical elements

### Micro

- scratches
- erosion
- fractures
- engravings
- particles
- eye texture
- material variation

Macro correctness always has priority over micro-detail.

## Provenance

Canonical art should retain:

- artSpecHash
- renderPlanHash
- model name
- model version
- model hash
- LoRA hashes
- seed
- sampler
- steps
- CFG
- resolution
- candidate media hash
- canonical media hash
