# Master Prompt Phase 12 — CLI Validation

Adds the read-only command `oxgad prompt-validate <path>`.

The command validates an `OX-MASTER-PROMPT-1` payload against the schema,
validation gates, quality profile, and canonical prompt hashing.

It does not generate images, execute model runtimes, publish assets, call
networks, or mutate project state.
