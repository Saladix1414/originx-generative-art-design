# Local Generator Phase 18 - Runtime Preflight CLI Inspection

This phase exposes a read-only CLI command:

    oxgad runtime-preflight

The command emits an OX-RUNTIME-PREFLIGHT-BUNDLE-1 payload.

The output remains blocked before execution. It does not construct an executable command, invoke a backend, run a model, access the network, or generate an image.
