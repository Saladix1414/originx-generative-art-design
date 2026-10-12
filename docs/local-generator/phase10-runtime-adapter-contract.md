# Local Generator Phase 10 — Runtime Adapter Contract

This phase defines `OX-RUNTIME-ADAPTER-1`.

The adapter is declared-only. It records intended runtime family and target, but
does not construct commands, invoke binaries, execute models, or generate media.

Default adapter intent:

- target: `LOCAL_CPP`
- runtime family: `stable-diffusion.cpp`
- executable path: null
- interface mode: `DECLARED_ONLY`
- backend invocation: false
- command construction: false

This phase does not execute models, call runtimes, generate media, call
networks, or approve canonical artwork.
