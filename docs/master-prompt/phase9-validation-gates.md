# Master Prompt Phase 9 — Validation Gates

Phase 9 adds local validation gates for `OX-MASTER-PROMPT-1`.

The gates detect:

- network URLs
- secrets-like terms
- celebrity/trademark/franchise terms
- download/upload instructions
- missing required negative prompt controls
- missing macro / meso / micro priorities
- missing local-first safety boundaries

These gates do not execute models, call network services, generate images, publish outputs, or move artifacts.
