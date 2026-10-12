# Local Generator Phase 77 - SD 1.5 runtime preflight plan

Defines one conservative runtime preflight for `OX-MODEL-002`.

The planned execution uses 256x256 resolution, one Euler step, batch size one,
four CPU threads, mmap, disk parameter backing, and tiled VAE decoding. Its
purpose is to prove that the model can load and produce one image without
crashing or restarting the device.

This is not the Tokens #0001-#0010 benchmark and cannot promote the model to
final production status.

## Required approval phrase

`I APPROVE OX-MODEL-002 SD15 SINGLE RUNTIME PREFLIGHT`
