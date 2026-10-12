# Local Generator Phase 87 — Profile 2 single-token executor

Adds a dedicated executor for one authorized attempt of Genesis Token #0001.

The executor binds the existing deterministic Token #0001 contracts to
OX-GENESIS-RENDER-PROFILE-2:

- 384x384
- 10 steps
- DPM++ 2M
- Karras scheduler
- CFG 7.0
- batch size 1
- lossless RGB8 PNG
- conservative disk-backed, memory-mapped runtime
- tiled VAE decoding

It verifies the exact model and runtime hashes and records authorization,
profile, gate, interruption evidence, runtime log, memory/thermal telemetry,
media evidence, and a hashed result.

The executor refuses overwrite and automatic retry. It cannot execute Token
#0002, upscale, canonicalize artwork, approve quality, or begin another batch.
