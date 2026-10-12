# Phase 84 - Genesis runtime seed compatibility

The pre-execution audit found that identity seeds for Tokens #0001, #0006,
and #0008 exceed the signed 64-bit range accepted by stable-diffusion.cpp.

Canonical identity seeds remain unchanged. Runtime seeds are derived with:

`runtimeSeed = identitySeed & 0x7fffffffffffffff`

This mapping is deterministic, preserves token identity evidence, produces
non-negative signed 64-bit seeds, and is recorded in every runtime binding.

No model execution occurred before this correction.
