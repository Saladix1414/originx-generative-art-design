# Local Generator Phase 93 — SD 1.5 FP16 VAE preflight executor

Adds a single-use executor for the explicitly authorized external FP16 VAE
preflight.

The executor verifies the model, runtime, and VAE hashes before generating one
256x256, one-step technical image. It uses non-tiled VAE decoding and records
runtime logs, memory evidence, thermal evidence, PNG evidence, and a hashed
result.

A valid PNG still requires manual inspection for vertical banding. This phase
does not authorize a Genesis retry or any canonical artwork.
