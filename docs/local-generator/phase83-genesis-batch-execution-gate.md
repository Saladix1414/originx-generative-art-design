# Phase 83 - Genesis batch execution gate

Defines the explicit execution boundary for GENESIS-BATCH-0001, Tokens
#0001-#0010.

Execution is sequential, batch size one, with memory and thermal checks,
per-token timeout, cooldown, and immediate stop on failure.

Approval authorizes candidate rendering only. It does not approve any image as
canonical, promote SD 1.5 to final production status, authorize retries, or
authorize GENESIS-BATCH-0002.

Required phrase:

`I APPROVE GENESIS-BATCH-0001 TOKENS 0001 THROUGH 0010`
