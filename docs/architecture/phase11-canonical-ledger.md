# Phase 11 — Canonical Ledger

Phase 11 adds a canonical ledger for promotion decisions.

The ledger records promotion decisions as deterministic JSON evidence. It preserves:

- canonical id
- candidate id
- promotion decision
- promotion schema version
- provenance manifest digest
- append index

The ledger does not move artifacts, write image outputs, publish canonical files, or execute models. It is a record boundary for later canonical output workflows.
