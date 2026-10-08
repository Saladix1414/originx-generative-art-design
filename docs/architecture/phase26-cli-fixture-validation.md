# Phase 26 — CLI Fixture Validation

Phase 26 adds a local CLI validation command.

`oxgad validate-fixture <path> --schema <schema>` validates a local JSON document against a local JSON schema and prints a small validation summary.

The command reads local files only. It does not write files, call networks, execute models, export artifacts, or publish outputs.
