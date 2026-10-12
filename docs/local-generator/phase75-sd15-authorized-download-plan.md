# Local Generator Phase 75 - SD 1.5 download plan

Defines the `AUTHORIZED_DOWNLOAD` path for the SD 1.5 Q4_0 artifact assigned
to candidate `OX-MODEL-002`.

The plan is pending explicit approval and grants no download or execution
authority.

## Required approval phrase

`I APPROVE OX-MODEL-002 SD15 Q4_0 ARTIFACT DOWNLOAD`

## Safety requirements

- Confirm at least twice the artifact size is free.
- Download to a `.part` path.
- Verify exact byte size and Git LFS SHA-256.
- Promote atomically only after both checks pass.
- Preserve a mismatching partial artifact as evidence.
- Do not execute the model after download.
- Require separate approval for a single runtime preflight.
- Require another decision before Tokens #0001-#0010.
