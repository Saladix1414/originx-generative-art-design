# Phase 85 - Genesis batch executor

Adds a resumable sequential executor for GENESIS-BATCH-0001.

The executor verifies model and runtime hashes, materializes deterministic
contracts, renders batch size one, records per-token logs and telemetry,
validates 512x512 PNG outputs, and stops on the first failure.

Completed candidates are never overwritten. Failed tokens are never silently
replaced. No candidate is marked canonical and no next batch starts
automatically.
