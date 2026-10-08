# Master Prompt Phase 14 — Prompt Provenance Hook

This phase creates a provenance-ready evidence hook for
`OX-MASTER-PROMPT-1`.

The hook records:

- master prompt hash;
- art spec hash;
- render plan hash;
- runtime target;
- seed;
- compiler version;
- provenance flags.

The hook is not canonical approval. It explicitly preserves that generated
AI output is not canonical art and still requires manual approval.
