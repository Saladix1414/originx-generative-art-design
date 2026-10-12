# Local Generator Phase 3 — Candidate Output Contract

This phase defines `OX-CANDIDATE-OUTPUT-1`.

A candidate output is explicitly not canonical. It records:

- render plan hash;
- execution decision hash;
- optional model binding hash;
- media path;
- media hash placeholder;
- dimensions placeholder;
- quality review state;
- authority boundaries.

This phase does not execute models, generate media, inspect media files, call
networks, or approve canonical artwork.
