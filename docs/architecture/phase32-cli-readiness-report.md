# Phase 32 — CLI Readiness Report

Phase 32 adds `oxgad readiness`.

The command summarizes local CLI readiness by checking:

- all registered schemas validate as JSON Schema
- mapped CLI fixtures validate
- the evidence chain length matches the registered contract count

The command is read-only and local-only.
