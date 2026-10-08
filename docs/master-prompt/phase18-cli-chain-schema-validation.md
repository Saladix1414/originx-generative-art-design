# Master Prompt Phase 18 — CLI Chain Schema Validation

This phase makes `oxgad prompt-chain <path>` validate the generated prompt
evidence chain against `schemas/ox-master-prompt-evidence-chain-1.schema.json`.

Successful output now includes:

- `valid: true`
- `schema_valid: true`

The command remains read-only and does not execute models, generate media, call
networks, mutate runtime state, or approve canonical artwork.
