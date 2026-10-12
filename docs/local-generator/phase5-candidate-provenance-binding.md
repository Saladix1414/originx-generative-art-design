# Local Generator Phase 5 — Candidate Provenance Binding

This phase defines `OX-CANDIDATE-PROVENANCE-HOOK-1`.

The hook links:

- candidate output hash;
- candidate manifest hash;
- execution decision hash;
- prepared media path.

It remains prepare-only:

- no media is generated;
- media hash is null;
- backend invocation is false;
- candidate is not canonical;
- manual approval remains required.

This phase does not execute models, generate media, inspect media files, call
networks, or approve canonical artwork.
