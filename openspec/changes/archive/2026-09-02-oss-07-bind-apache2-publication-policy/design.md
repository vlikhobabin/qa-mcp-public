## Context

The clean baseline already records operator approval for SPDX `Apache-2.0`
and publishes OSS-07-I2, but has no LICENSE/NOTICE or exact public-history
boundary. Existing Git history contains personal author metadata and historical
lab identifiers, so publishing all ancestors cannot satisfy the card's privacy
criterion even after the current tree is sanitized.

## Goals / Non-Goals

**Goals:**

- Bind one exact license in canonical legal text and package metadata.
- Define a source-snapshot publication boundary whose included tree is audited
  and whose excluded ancestors remain internal migration history.
- Use GitHub Issues and private vulnerability reporting as role-based contacts.
- Preserve I2's exact files and verifier as a mandatory gate.

**Non-Goals:**

- Publish a GitHub/GHCR release, rewrite current Git history or cut over a
  private downstream.
- Restore any I1 byte or change I2 semantics.
- Run any live/platform/Windows verification.

## Decisions

1. `LICENSE` carries the unmodified Apache License 2.0 text, `NOTICE` carries
   project/trademark attribution, and `pyproject.toml` uses the PEP 639 SPDX
   expression `Apache-2.0`. No dual-license or future-license placeholder is
   accepted.
2. `config/publication-policy.json` is the machine authority; a human-readable
   `docs/publication-policy.md` explains it. Public history begins from one
   audited snapshot created by later publication work. Existing ancestors are
   reviewed as excluded input, not claimed safe for public import. Rewriting or
   publishing that snapshot belongs to OSS-08.
3. Contacts are repository roles and GitHub UI routes, never an individual's
   email, host or account credential.
4. The policy names the exact published I2 matrix/freeze/helper/verifier paths
   and requires `verify_matrix.py --run-mutations`. The audit hashes those files
   so any change must go through a new reviewed payload.

Alternatives rejected: publishing all current ancestors (personal/private lab
metadata), inventing a maintainer email (no approval), or copying I1 (explicitly
forbidden and technically unavailable).

## Risks / Trade-offs

- [Risk] Snapshot history loses internal commit-by-commit provenance. -> The
  public provenance manifest binds every published asset byte, while excluded
  internal Git remains separately retained by the owner.
- [Risk] NOTICE trademark wording could imply endorsement. -> State nominative
  use and no affiliation or endorsement.
- [Risk] I2 drift could silently weaken the gate. -> Bind exact paths/digests
  and run all 23 hostile mutations.

## Migration Plan

Add policy/legal metadata first, validate exact SPDX consistency, then allow
later OSS-07 changes to consume it. Rollback removes only this change's files
and metadata; it does not touch published I2 or Git history.

## Capture, Replay And Cleanup

No protocol capture, frame range, replay, dynamic runtime field or process is
used. Checks read repository bytes only and create temporary files solely under
owned ignored state, which they remove on exit.

## Open Questions

- none.
