# Phase 9 — Quality Gates

Phase 9 adds deterministic local quality gates for candidate artwork evidence.

The quality gate report checks that a candidate has:

- a stable candidate id
- a valid provenance manifest digest
- an output artifact SHA-256 digest
- model registry and binding references
- local forge render request and backend references
- art spec identity evidence

Advisory gates can flag incomplete creative evidence without blocking required provenance acceptance.

This phase does not execute models, does not inspect binary artwork, does not call external services, and does not publish final canonical output.
