# Local Generator Phase 92 — SD 1.5 FP16 VAE preflight plan

Defines one conservative technical preflight for the acquired official SD 1.5
FP16 VAE.

The preflight is limited to 256x256, one sampling step, batch size one, and
non-tiled VAE decoding. It verifies that the external VAE loads and produces a
valid RGB8 PNG without the critical vertical-banding defect.

The preflight is not a Genesis candidate and cannot authorize another retry,
canonicalization, Token #0002, or another batch.

Exact authorization phrase:

`I APPROVE OX-MODEL-002 SD15 FP16 VAE SINGLE PREFLIGHT`
