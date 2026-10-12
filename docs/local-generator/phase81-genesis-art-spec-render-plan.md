# Phase 81 - Genesis Art Specs and Render Plans

Prepares deterministic OX-ART-SPEC-1 and OX-RENDER-1 plans for Genesis
#0001-#0010 using the existing Structure Engine and Render Compiler.

A separate OX-GENESIS-RENDER-BINDING-1 envelope fixes:

- OX-MODEL-002
- the verified SD 1.5 Q4_0 model hash
- stable-diffusion.cpp runtime identity
- 512x512 resolution
- batch size one
- 12 Euler Ancestral steps
- conservative mmap, disk-backed parameters and VAE tiling

The canonical OX-RENDER-1 plan remains execution-disabled. The binding also
remains disabled until the benchmark execution phase.

No candidate is canonical and no model execution occurs in this phase.
