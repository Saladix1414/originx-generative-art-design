# Phase 18 — Local Export Executor

Phase 18 introduces the controlled local export executor.

The executor requires a ready dry run before it writes anything. It writes the canonical output manifest and copies one explicit artifact source into the planned output/canonical path.

The executor rejects absolute paths, parent traversal, and any destination outside output/canonical.
