# Local Generator Phase 89 — Token #0001 technical retry executor

Adds a single-use executor for the explicitly authorized technical retry of
Genesis Token #0001.

All deterministic identity and creative generation inputs remain unchanged.
The only processing change is removal of tiled VAE decoding. The retry uses
non-tiled VAE decoding to isolate the severe vertical-banding defect observed
in the rejected candidate.

The executor verifies the source candidate, model, runtime, approval phrase,
memory, and thermal limits. It refuses overwrite and any second retry.

A successful runtime result remains only a candidate pending manual Quality
Gate review. It cannot authorize canonicalization, upscale, Token #0002, or
another batch.
