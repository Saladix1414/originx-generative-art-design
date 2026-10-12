# Local Generator Phase 2 — Execution Decision Binding

This phase binds an `OX-LOCAL-FORGE-1` contract to an
`OX-LOCAL-FORGE-EXECUTION-DECISION-1` decision.

The decision remains conservative:

- decision is `DENY`;
- backend invocation is false;
- model execution is not allowed;
- media generation is not allowed;
- canonical artwork approval is not allowed.

This phase does not execute a model, call a runtime, generate media, call
networks, or approve canonical artwork.
