# OriginX Render Compiler — Phase 4 Closure

## Status

PHASE 4 — OriginX Render Compiler is complete.

The phase establishes the deterministic boundary between canonical structured art intent and future image-generation runtimes.

No model was installed or executed during PHASE 4.

## Canonical pipeline

```text
OX-ART-SPEC-1
+ artSpecHash
+ artRuleHash
+ designHash
        ↓
OriginX Render Compiler
        ↓
OX-RENDER-1
+ renderPlanHash
```

## Canonical versions

- OX-ART-SPEC-1
- OX-RENDER-1
- OX-RENDER-COMPILER-1
- OX-RENDER-FIRST10-MANIFEST-1

## OX-RENDER-1 responsibilities

The Render Plan contains structured downstream rendering intent including:

- source evidence
- identity evidence
- structured prompt program
- structured negative program
- camera
- composition
- materials
- sampling policy
- resolution
- model binding boundary
- conditioning slots
- detail policy
- upscale policy
- execution policy

The contract is closed with `additionalProperties: false`.

## Source evidence

Every compiled Render Plan binds:

- artSpecHash
- artRuleHash
- designHash
- seed

Compilation fails closed when these values disagree with deterministic source evidence.

## renderPlanHash

`renderPlanHash` is the canonical SHA-256 hash of the validated OX-RENDER-1 plan.

It identifies the Render Plan, not generated media.

```text
RENDER PLAN HASH != MEDIA HASH
```

The future candidate media hash and canonical media hash remain downstream concerns.

## Prompt program boundary

The PHASE 4 prompt program is structured and deterministic.

It is not a Stable Diffusion prompt, provider prompt or model-specific command.

```text
STRUCTURED PROMPT PROGRAM != PROVIDER PROMPT
```

Provider-specific compilation remains downstream from canonical render truth.

## Sampling boundary

Sampling remains non-executable in PHASE 4.

The sampler remains `UNBOUND`; PHASE 4 does not claim a real runtime sampler or model configuration.

Runtime-specific tuning belongs to later hardware, forge and model phases.

## Model binding boundary

PHASE 4 requires:

```text
status       = UNBOUND
modelName    = null
modelVersion = null
modelHash    = null
```

This prevents fabricated model identity before the Model Registry exists.

## Conditioning boundary

LoRA and ControlNet are represented only as future binding slots.

PHASE 4 does not load, execute or claim any conditioning asset.

## Detail authority

```text
MACRO > MESO > MICRO
```

Macro anatomy, silhouette, physical mass and composition retain authority over microdetail.

Microdetail cannot be used to conceal invalid anatomy.

## Execution governance

Every PHASE 4 Render Plan enforces:

```text
policy              = LOCAL_FIRST
providerIndependent = true
executionAllowed    = false
target              = UNBOUND
```

Therefore the Render Compiler describes rendering intent but has no authority to execute it.

## First-10 evidence

The canonical first ten Founding-6000 identities compile reproducibly into ten unique Render Plans and ten unique renderPlanHash values.

The snapshot is stored in:

`docs/architecture/phase4d-first-10-render-manifest.json`

The manifest binds identity, DNA hash, seed, Art Spec hash, Art Rule hash, design hash and Render Plan hash.

## Historical preservation

PHASE 4 does not modify OX-ART-SPEC-1 or historical PHASE 2 Art Specs.

The PHASE 2 first-ten manifest and Art Spec hashes remain unchanged.

## Governance invariants

```text
AI OUTPUT != CANONICAL ART
CANDIDATE != APPROVED ART
SEED != FULL REPRODUCIBILITY
MODEL NAME != MODEL IDENTITY
MODEL FILE != TRUSTED MODEL
HIGH DETAIL != HIGH QUALITY
QUALITY SCORE != FINAL AUTHORITY
EXTERNAL PROVIDER != CANONICAL DEPENDENCY
RENDER PLAN HASH != MEDIA HASH
```

## Explicit non-goals

PHASE 4 does not implement:

- hardware detection
- model installation
- model registry binding
- Stable Diffusion execution
- LoRA execution
- ControlNet execution
- GPU inference
- image generation
- image upscale execution
- candidate media hashing
- canonical media approval
- provider execution

## Next phase

```text
PHASE 5 — Hardware Detection
```

Hardware detection may describe available execution capability, but hardware availability does not grant execution authority.
