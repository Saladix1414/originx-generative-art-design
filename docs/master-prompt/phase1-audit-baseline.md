# Master Prompt Phase 1 — Audit / Baseline

This phase starts the Master Prompt roadmap from a clean baseline.

## Current Repo Authority

The current repository already contains the canonical foundations required before prompt construction:

- OX-ART-SPEC-1 schema
- OX-ART-SPEC validator
- canonical art spec hashing
- OriginX Structure Engine
- OriginX Render Compiler
- OX-RENDER-1 schema
- art spec expansion schema
- art spec expansion catalog
- art spec expansion loader
- provenance and quality evidence chain

## Master Prompt Position

The Master Prompt is not the source of truth.

The source of truth remains:

structured identity
+
OX-ART-SPEC-1
+
OX-RENDER-1
+
model identity
+
generation parameters
+
media hashes
+
provenance

The Master Prompt is a compiled render instruction artifact derived from structured contracts.

## Controlled Vocabulary Baseline

The Master Prompt system must use the controlled vocabulary from:

`config/art-spec-expansion-catalog.json`

Baseline vocabulary groups:

- trait families
- rarity bands
- composition profiles
- render intents

## Future Master Prompt Payload

A future Master Prompt payload should bind:

- identity input
- art spec hash
- render plan hash
- trait family evidence
- rarity band
- composition profile
- render intent
- positive prompt text
- negative prompt text
- macro detail priorities
- meso detail priorities
- micro detail priorities
- local-first safety boundaries
- provenance hooks

## Boundaries

This phase is audit-only.

It does not create the Master Prompt schema, build prompt strings, execute models, call network services, download assets, publish outputs, or move generated artifacts.
