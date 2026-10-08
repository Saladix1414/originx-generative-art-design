# Release Notes Draft — Phase 8-35 Local Evidence Pipeline

This draft summarizes the local evidence pipeline added across Phase 8 through Phase 35.

## Scope

The project now includes a local-first evidence chain for generative art candidates:

- provenance manifest
- quality gate report
- canonical promotion decision
- canonical ledger
- canonical output manifest
- review pack
- release readiness decision
- release ledger
- local export plan
- local export dry run
- local export executor
- export audit ledger
- project readiness summary

## CLI

The local `oxgad` CLI can inspect and validate the pipeline:

- schema
- status
- validate-fixture
- validate-fixtures
- contracts
- validate-contracts
- evidence-chain
- readiness
- version
- stability

## Boundaries

The implemented pipeline remains local-first.

It does not introduce remote publishing, package publishing, minting, network workflows, model execution, uncontrolled artifact movement, or automatic upload behavior.

## Verification

The release draft is backed by regression tests covering schemas, evidence chaining, CLI fixtures, CLI contract validation, readiness reporting, help surface, version output, and stability summary.
