# Local Generator Phase 90 — SD 1.5 external FP16 VAE plan

The embedded Q4_0 VAE produced severe vertical banding with both tiled and
non-tiled decoding. Phase 90 selects an external FP16 VAE for source-controlled
technical isolation.

## Selected artifact

- Component ID: `OX-MODEL-002-VAE-FP16-1`
- Repository: `stable-diffusion-v1-5/stable-diffusion-v1-5`
- Revision: `451f4fe16113bff5a5d2269ed5ad43b0592e9a14`
- File: `vae/diffusion_pytorch_model.fp16.safetensors`
- Size: 167335342 bytes
- SHA-256:
  `4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c`
- License: CreativeML OpenRAIL-M
- Format: safetensors
- Precision: FP16
- Source is public and not gated.

This is the smallest audited official SD 1.5 VAE and retains the same upstream
source and license family as the base model.

The external VAE is a runtime component, not a replacement of Token #0001,
its identity, DNA, Resonance, Glyph, Art Spec, seed, prompt, or Q4_0 diffusion
weights.

No download is authorized by this plan. Exact approval is required:

`I APPROVE OX-MODEL-002 SD15 FP16 VAE ARTIFACT DOWNLOAD`
