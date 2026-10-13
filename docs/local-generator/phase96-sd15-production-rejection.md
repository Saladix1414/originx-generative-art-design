# Local Generator Phase 96 — OX-MODEL-002 production rejection

Stable Diffusion 1.5 Q4_0 (`OX-MODEL-002`) is formally rejected for OriginX
local production.

Three controlled full representative generations produced the same dominant
vertical-banding artifact:

1. embedded Q4_0 VAE with tiled decoding;
2. embedded Q4_0 VAE with non-tiled decoding;
3. official external FP16 VAE with non-tiled decoding.

Model, prompt, negative prompt, deterministic seed, sampler, scheduler, steps,
CFG, and resolution remained constant. Replacing the VAE did not remove the
defect, so the VAE is not accepted as the demonstrated principal cause.

Potential failure domains remain the Q4_0 diffusion weights, backend/runtime,
quantization, or their interaction. No unsupported single root cause is
asserted.

The dominant artifact prevents evaluation of anatomy, composition, materials,
detail, visual identity, and Art Spec adherence. Technical Gate and Visual Gate
both fail; quality is 0/100.

`OX-MODEL-002` now has status `REJECTED_FOR_PRODUCTION`. Its role and production
alias are null. `OX-GENESIS-MODEL-1` remains `UNASSIGNED`.

All artifacts, candidates, hashes, prompts, seeds, sampling settings, runtime
identity, telemetry, receipts, and comparison evidence are preserved. Further
renders, retries, downloads, upscale, canonicalization, Token #0002, and silent
weight substitution are prohibited.

## Permanent acceptance invariant

`ONE_STEP_PREFLIGHT != PRODUCTION_VALIDATION`

Every future model must pass, in order:

1. hardware preflight;
2. minimal inference preflight;
3. full representative generation;
4. image integrity inspection;
5. visual quality gate;
6. only then production promotion.
