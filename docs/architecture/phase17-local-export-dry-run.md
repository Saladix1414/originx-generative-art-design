# Phase 17 — Local Export Dry Run

Phase 17 evaluates whether a local export plan is ready to execute.

The dry run checks:

- export plan status is planned
- artifact source path is present
- planned output paths stay under output/canonical

This phase does not create directories, copy files, move artifacts, write manifests, publish outputs, or execute models.
