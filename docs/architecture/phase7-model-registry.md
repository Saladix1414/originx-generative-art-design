# OriginX Model Registry — Phase 7

## Status

PHASE 7 establishes canonical model identity, artifact evidence, trust evidence, and verified model binding.

Core governance:

- MODEL NAME != MODEL IDENTITY
- MODEL FILE != TRUSTED MODEL
- REGISTRATION != EXECUTION AUTHORITY
- VERIFIED != EXECUTION AUTHORITY
- MODEL BINDING != EXECUTION AUTHORITY

Canonical contracts:

- OX-MODEL-REGISTRY-1
- OX-MODEL-IDENTITY-1
- OX-MODEL-TRUST-EVIDENCE-1
- OX-MODEL-BINDING-1

Model identity and artifact identity remain separate.

A logical model identity contains modelId, name, family, version, and identityHash.

Artifact evidence contains sha256, format, and sizeBytes.

Trust states are:

- UNVERIFIED
- VERIFIED
- REJECTED

Artifact verification is deterministic.

Matching artifact evidence may produce VERIFIED.

Mismatched evidence produces REJECTED.

Evidence is bound to model identity and artifact hash.

Cross-model replay is rejected.

Cross-artifact replay is rejected.

Model binding requires a VERIFIED model with a HASH_BOUND artifact.

Binding is context-bound to:

- model identity
- artifact hash
- trust evidence hash
- renderPlanHash
- requested local target

Cross-render-plan replay is rejected.

Cross-target replay is rejected.

Binding governance requires:

- bindingGrantsExecutionAuthority = false
- executionAllowed = false
- backendInvocationAllowed = false

The Local Forge request itself remains UNBOUND.

The Local Forge execution boundary remains DENY.

PHASE 7 performs no model download, installation, loading, inference, or image generation.

Next phase:

PHASE 8 — First Local Model

PHASE 8 may introduce the first real local model artifact, but registration, trust, binding, and execution authority must remain separate.
