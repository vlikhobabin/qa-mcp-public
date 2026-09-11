## Context

The S4-R1 outer runner proved its session-0 preflight, registered and started
the exact `InteractiveToken`/`Limited` task, and cleaned the task and stage,
but the session-1 preflight receipt was absent. The retained evidence does not
locate the failure between task-token identity, the first file snapshot/read,
final metadata restoration, and receipt writing. Reading the real 1C
configuration to disambiguate those phases is explicitly forbidden for this
investigation.

The investigation therefore uses a new exact-owned stage, exact-owned
disposable probe files, one uniquely named limited interactive task, and
privacy-safe receipts. There are no protocol frames or UI capture sources:
the only observations are typed status codes, booleans, bounded counts, script
hashes, and hashes of already-retained immutable S4-R2 inputs. Dynamic stage
names, raw paths, exception text, credentials, and UI data are not retained.

## Goals / Non-Goals

**Goals:**

- Establish whether the exact limited session-1 token can snapshot, read, and
  restore `LastAccessTimeUtc` on its own disposable file and write a receipt.
- Distinguish `snapshot_read_failure`, `metadata_set_authority_failure`,
  `task_token_mismatch`, and `evidence_write_failure` without raw diagnostics.
- Prove the same owner/worker chain in session 0 and session 1, plus exact
  task, stage, and stage-bound process cleanup.
- Select a least-authority owner for any future real-target snapshot and final
  restoration.

**Non-Goals:**

- Opening or reading the real 1C configuration, starting 1C, or invoking any
  S3, S4, S5, or S7 path.
- Changing production code, fixtures, the blocked S4-R1 payload, or public
  route behavior.
- Treating a disposable pass as S4-R1 live admission or as proof of authority
  over the real configuration.

## Decisions

### Use one probe owner/worker chain in both sessions

One session owner and one child worker receive only an exact-owned probe,
expected session id, and exact-owned receipt locations. For each invoked probe
reader, its first operation obtains the file item and immediately snapshots
`LastAccessTimeUtc`. All reads occur inside a protected region; restoration
occurs in `finally` and is the sole final probe operation, with no later probe
read. The owner observes the child's restoration before performing its own
final restoration. Receipt writes target separate exact-owned files. The outer
runner initializes probes without reading them and only deletes them during
exact-stage cleanup. A structural proof parses the owner, worker, and runner
before remote execution.

This avoids comparing different implementations between the session-0 control
and session-1 task and prevents an outer verifier from weakening the final-read
invariant after the child returns.

### Classify with receipt status plus bounded exit code

The worker writes a typed receipt when evidence storage is available. If the
receipt itself cannot be written, its bounded process exit code maps to
`evidence_write_failure`; the task wrapper records only that code mapping.
Token mismatch is decided before any probe access. Snapshot/read and metadata
set phases have distinct typed outcomes. No exception message, path, account
secret, timestamp value, or UI value is serialized.

### Session 0 owns real-target metadata restoration

The least-authority design assigns any future real-target first snapshot and
sole final restoration to the session-0 outer broker. Session 1 may consume
only exact-owned staged inputs and privacy-safe expected hashes; it does not
open, read, write, or restore the real configuration. This design is selected
even if the disposable session-1 probe passes, because a pass proves only the
limited token's authority over its own file and cannot safely generalize to a
protected real target.

An alternative that grants session 1 bounded metadata authority over the real
target is rejected: it expands authority, depends on target-specific ACL and
privilege behavior that this card is forbidden to inspect, and repeats the
missing-receipt failure surface. An alternative that infers restoration from a
later real-target read is also rejected because it violates the no-later-read
invariant.

### Retain a non-admitting evidence summary

Raw scripts and dynamic receipts remain in ignored card-owned runtime evidence.
The tracked report records only schemas, typed outcomes, booleans, bounded
counts, hashes, the selected design, cleanup results, and preservation checks.
There is no replay: re-verification reruns the structural proof and, only under
the same explicit operator authority, may rerun the disposable matrix against
the one allowed endpoint.

## Risks / Trade-offs

- **A disposable pass does not prove real-target ACL authority.** The decision
  does not generalize it; session 0 remains the real-target owner.
- **An absent receipt could otherwise remain ambiguous.** The bounded exit-code
  fallback separates evidence-write failure from the earlier typed phases.
- **Scheduled-task cleanup could affect unrelated state.** The runner creates,
  stops, queries, and unregisters only its exact unique task and compares a
  privacy-safe unrelated-task-set hash before and after.
- **A remote interruption could strand owned state.** The outer runner uses
  `finally`, removes only its exact stage and task, and reports nonzero exact
  residue as a blocker.
- **Existing shared-worktree changes could be staged accidentally.** The
  delivery manifest lists only the investigation card, report, synced spec,
  and archived artifacts; staging remains explicit and scope-checked.
