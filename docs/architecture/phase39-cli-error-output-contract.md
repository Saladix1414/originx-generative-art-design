# Phase 39 — CLI Error Output Contract

Phase 39 locks expected CLI validation error output.

Validation failures must return exit code 2 and machine-readable JSON on stdout, with no stderr stacktrace for normal validation failures.
