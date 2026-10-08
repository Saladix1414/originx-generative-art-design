# Master Prompt Phase 2 — Contract

Phase 2 defines the first Master Prompt contract: `OX-MASTER-PROMPT-1`.

The Master Prompt remains a derived render instruction artifact. It is not the source of truth and does not replace OX-ART-SPEC-1 or OX-RENDER-1.

The contract binds:

- identity input id
- art spec hash
- render plan hash
- controlled vocabulary
- render intent
- positive prompt text
- negative prompt text
- macro / meso / micro detail priorities
- local-first safety boundaries
- provenance hooks

This phase does not build prompt strings, execute models, call network services, download assets, publish outputs, or move generated artifacts.
