# Local Generator Phase 88 — Token #0001 technical rejection

The first Profile 2 candidate was generated successfully at the runtime level,
but failed the visual Quality Gate because severe vertical banding covers the
entire frame.

## Decision

- State: `REJECTED_TECHNICAL_ARTIFACT`
- Quality target: 92
- Quality Gate: failed
- Canonical approval: forbidden
- Upscale: forbidden
- Token #0002: blocked
- Next batch: blocked

The PNG container, CRCs, compressed stream, RGB8 dimensions, and complete pixel
decode were verified. Therefore the visible bands are part of the generated
pixel output rather than a gallery or file-transfer problem.

The latent sampling completed normally. Evidence currently points to the tiled
VAE decode, but root cause is not yet considered confirmed.

## Identity preservation

Token #0001 keeps the same canonical name, DNA, Resonance, Glyph, Art Spec,
Render Plan evidence, model, prompt, and deterministic seed. This is not an
identity failure and no creative reroll is allowed.

## Controlled retry plan

One technical isolation retry is prepared. It preserves all generation inputs
and changes only VAE decode from tiled 128x128 to non-tiled.

It requires this exact approval:

`I APPROVE GENESIS-BATCH-0001 TOKEN 0001 TECHNICAL RETRY 1`

This phase does not execute the retry and does not grant authority for another
token.
