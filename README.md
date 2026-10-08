# OriginX Generative Art Design

OriginX Generative Art Design is the independent generative visual platform for the OriginX universe.

## Core systems

- OriginX Generative Art Engine — OX-GAE
- OriginX Structure Engine
- OriginX Render
- OriginX Local Forge
- OriginX Detail Engine
- OriginX Quality Engine
- OriginX Provenance Engine

## Canonical pipeline

Identity Input
→ Structured Art Specification
→ Render Plan
→ Local Forge
→ Candidate Artwork
→ Detail Passes
→ Quality Gate
→ Canonical Artwork
→ Provenance

## Initial versions

- Project: OX-GAD-1
- Engine: OX-GAE-1
- Art Spec: OX-ART-SPEC-1
- Render Plan: OX-RENDER-1

## Principles

- structured generation before prompt generation
- local-first execution
- provider-independent architecture
- deterministic identity inputs
- reproducible provenance
- extreme visual detail
- anatomy before decoration
- candidate artwork is never automatically canonical

## Local CLI

Install the project locally in editable mode:

    python -m pip install -e .

Inspect local JSON evidence:

    oxgad schema tests/fixtures/cli/project-readiness-summary.json
    oxgad status tests/fixtures/cli/canonical-promotion.json

Validate local fixtures and contracts:

    oxgad validate-fixtures tests/fixtures/cli
    oxgad validate-contracts

Inspect the local evidence pipeline:

    oxgad contracts
    oxgad evidence-chain
    oxgad readiness
    oxgad version
    oxgad stability

The CLI is local-first and read-only for inspection commands. It does not execute models, call network services, publish packages, upload artifacts, mint assets, or perform uncontrolled artifact movement.
