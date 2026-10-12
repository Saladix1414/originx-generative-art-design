# Local Generator Phase 7 — Candidate Dry Run Builder

This phase builds a complete prepare-only candidate dry run:

`Execution Decision → Candidate Output → Candidate Manifest → Candidate Provenance Hook`

The dry run records all hashes and authority boundaries.

It remains non-executing:

- backend invocation is false;
- media is not generated;
- media hash remains null;
- candidate is not canonical;
- manual approval remains required.

This phase does not execute models, generate media, inspect media files, call
networks, or approve canonical artwork.
