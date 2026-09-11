# Investigate Session-1 Last-Access Restoration Authority

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i1

## Order Index
405.1015

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`

## Summary
Determine why the exact limited interactive session-1 preflight cannot produce
its receipt after structurally correct first-snapshot/final-restore ordering,
and define a fail-closed ownership design before S4-R1 receives any further
real-configuration or live-row admission.

## Source Lineage
- Blocked source card:
  `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`.
- Latest safe published composition:
  `ceb5778ed5a9a48006443b3cd6a2d7598f7fc60b` plus only the seven declared
  S4-R1 Go paths.
- First blocker: the older session-1 preflight read the real configuration but
  did not restore `LastAccessTimeUtc` when it stopped early.
- Repeated blocker: the v2 preflight passed all structural and session-0
  disposable gates, then the limited session-1 task stopped before emitting a
  preflight receipt; the live runner and every S3/S4/S5 row remained unstarted.
- Retained evidence:
  `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-diagnostic-20260901t1157z/blocker.json`
  and
  `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-admission-20260901t1740z/blocker.json`.

## Acceptance
- Reproduce and classify the session-1 failure using only an exact-owned
  disposable temp file under the limited interactive task; do not open the
  real 1C configuration or start 1C.
- Retain a typed, privacy-safe distinction between snapshot/read failure,
  metadata-set authority failure, task-token mismatch and evidence-write
  failure without storing raw paths, error text, credentials or UI data.
- Decide whether session 1 can safely own final access-time restoration. If it
  cannot, specify an exact-owned design that removes real-configuration reads
  from session 1 or establishes a reviewed bounded authority without weakening
  the least-privilege live runner.
- Prove every invoked script structurally snapshots before any read, restores
  through `finally` as the sole final file operation and performs no later
  file read; dynamically prove the selected design in session 0 and session 1
  on disposable files.
- Preserve zero action, exact task/stage/process cleanup, all four immutable
  S4-R2 hashes and protected S7/fixtures/OSS-07/OSS-08 bytes.
- Produce a fresh independent review before the source S4-R1 card can receive
  another bounded historical-user-only confirmation.

## Change Set
1. `investigate-session1-last-access-restoration-authority`

## Verify
- `.runtime/changerail/evidence/oss-06-s4-r1-i1-investigate-session1-last-access-restoration-authority/index.json`:
  `rescue1-structural-proof`, `rescue1-disposable-session-matrix`,
  `rescue1-protected-postflight`, and `rescue1-remote-postflight` passed.
- The exact session owner, child worker, and outer runner passed Windows AST
  parsing plus local all-script structural proof; session 0 and exact limited
  session 1 both passed disposable snapshot/read/restoration/receipt checks
  with the same owner and worker hashes.
- Typed exit mappings `51` through `54`, immutable S4-R2 hashes, blocked S4-R1,
  protected S7/fixture/OSS-07/OSS-08, parent manifest, and empty staging were
  verified without reading the real configuration or starting 1C.
- Strict change/all OpenSpec, manifest scope, public privacy scan, and
  `git diff --check` are the final review handoff floor.

## Archive
- `openspec/changes/archive/2026-09-01-investigate-session1-last-access-restoration-authority/`

## Related
- `openspec/changes/archive/2026-09-01-investigate-session1-last-access-restoration-authority/`
- `docs/protocol-research/evidence/session1-last-access-restoration-authority-2026-09-01/findings.md`
- `openspec/specs/qa-mcp-session1-metadata-restoration-authority/spec.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md`

## Result
The missing receipt did not reproduce on exact-owned disposable files: the
same owner/worker chain passed in session 0 and the exact limited session-1
task, including snapshot, read, final access-time restoration and receipt
write. Typed token,
snapshot/read, metadata-set and evidence-write boundaries are now distinct.
The least-authority decision keeps any real-target first snapshot and sole
final restoration in session 0 and forbids session-1 real-configuration access.
No 1C process, live row, S7 route, action or admission was started.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-session1-last-access-restoration-authority`

### Why
Static ordering and a session-0 disposable proof are insufficient to establish
that the limited session-1 token can restore file metadata and emit its receipt.

### Goal
Establish the exact failure boundary and a reviewable least-authority ownership
design without touching the real configuration.

### Scope
- Disposable session-0/session-1 metadata-operation investigation.
- Typed privacy-safe diagnostics for the preflight boundary.
- Design and hostile proofs only; no S3/S4/S5 live row and no S7 route.

### Acceptance
- The failure is reproducible or safely ruled out under the exact limited task
  token, and the selected ownership design passes both disposable sessions.
- No result from this card is itself S4-R1 live admission.

### Depends On
- none

### Related
- `openspec/changes/investigate-session1-last-access-restoration-authority/`

## Log
- 2026-09-01 created as the mandatory investigation handoff after the repeated
  session-1 configuration-metadata preflight blocker; no retry was performed.
- 2026-09-01 fast-forwarded one bounded documentation/OpenSpec investigation
  change with a disposable-only Windows proof matrix and session-0-owned
  least-authority restoration design; no 1C or real-configuration access was
  planned.
- 2026-09-01 exact historical-user disposable proof passed in session 0 and the limited
  session-1 task with typed privacy-safe boundaries and exact task/stage/process
  cleanup. A recorder encoding defect required one cleanly separated rerun;
  exact postflight was green before and after. No real configuration or 1C
  process was accessed or started.
- 2026-09-01 synced the new session-0 ownership capability, archived the
  completed investigation change, and left the card in progress for the fresh
  independent review gate.
- 2026-09-01 corrected review routing: the repeated metadata-preflight defect
  belongs to the blocked parent and is this card's source; this zero-production
  investigation is the required investigation/simplification payload, not a
  repeated-defect implementation rescue.
- 2026-09-01 review cycle 1 returned `NO-GO`: the outer matrix runner weakened
  the all-invoked-script final-read invariant and two unusable early recorder
  artifacts were still marked mandatory. Same-card rescue attempt 1 introduced
  one shared session owner/worker chain, removed all outer probe reads, reran
  the exact limited historical-user disposable matrix, corrected the evidence ledger,
  and preserved every protected hash and zero-action cleanup invariant.
- 2026-09-01T13:27:27Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
