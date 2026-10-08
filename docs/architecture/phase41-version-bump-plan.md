# Phase 41 — Version Bump Plan

Phase 41 defines the version bump plan after the Phase 8-40 local pipeline maturity block.

## Current Version

The current package version is `0.23.0`.

## Planned Version

The next planned package version is `0.41.0`.

## Rationale

The Phase 8-40 block added a mature local-first evidence pipeline and CLI inspection surface:

- provenance through project readiness
- local export planning, dry run, execution, and audit evidence
- CLI fixtures, contract reporting, contract validation, readiness, version, stability, JSON output contract, and error output contract
- documentation for maturity and release notes

## Boundary

This phase is planning only. It does not change package metadata, publish packages, upload artifacts, execute models, call network services, or move generated assets.

## Execution

The actual version bump should happen in Phase 42 by updating `pyproject.toml`, package metadata tests, CLI version tests, and related documentation in one exact-file commit.
