# Local Generator Phase 86 — Genesis Render Profile 2

Phase 86 records the interrupted initial render of Token #0001 and defines a
faster conservative profile for a new single-token trial.

## Interrupted attempt

The original 512x512, 12-step Euler Ancestral attempt reached observed sampling
progress 5/12. Telemetry reached 771 seconds and showed a minimum observed
MemAvailable value of 644212 kB. The user stopped the attempt to optimize its
runtime profile.

No candidate image was produced. This is not classified as a token, model, or
quality failure. Token #0001 retains its identity and remains eligible for a
controlled retry.

## Render Profile 2

- Scope: Token #0001 only
- Resolution: 384x384
- Steps: 10
- Sampler: DPM++ 2M
- Scheduler: Karras
- CFG: 7.0
- Batch size: 1
- Output: lossless RGB8 PNG
- VAE: tiled at 128x128
- Upscale: deferred until manual Quality Gate approval
- Intended upscale target: 1024x1024

RGB8 is the canonical candidate encoding because the SD 1.5 output pipeline does
not create additional source information by converting the image to 16 bits.
PNG remains lossless.

Identity, DNA, Resonance, Glyph, Art Spec, deterministic identity seed, and
existing Akashic history are unchanged. The runtime profile is separately
versioned and hashed.

## Authorization boundary

No execution is authorized by this phase. A new exact approval is required:

`I APPROVE GENESIS-BATCH-0001 TOKEN 0001 RENDER PROFILE 2`

The gate authorizes at most one candidate attempt for Token #0001. It does not
authorize Token #0002, canonicalization, automatic retry, upscale, or another
batch.
