# Phase 27 — CLI Validation Errors

Phase 27 makes fixture validation failures machine-readable.

Invalid fixtures return:

- exit code 2
- JSON output with `valid: false`
- schema version
- schema id
- validation error message

This keeps CLI validation useful in local scripts without exposing Python stack traces during normal validation failures.
