# Hidden direct-execute main-window investigation

## Decision

S7 remains blocked. The retained evidence does not establish that the tracked
EPF creates an admitted hidden main window or reaches passive UIA. It records
several exact-contour pre-admission outcomes and requires a bounded S4
replacement: stabilize the worker/job/desktop observation lifetime, require a
structurally validated main-window receipt, and only then bind the expected
marker to a passive UIA hash from the exact tracked fixture.

The replacement is tracked by
`oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle`. It may
change only the inherited lifecycle/observation boundary and its tests. It
does not admit the S7 public route, perform a prompt action or weaken the S4
window and topology gates.

## Exact contour

- Access: `ssh historical-user`, equivalent to `historical-user@192.0.2.201`; no other
  Windows SSH target is part of this evidence.
- Host and principal: `HISTORICAL-LAB-HOST\historical-user`, interactive session `1`.
- Platform: Windows 1C `8.3.27.2214`.
- Test candidate SHA-256:
  `3239e8166654cfc5eaa51d6993b46c89b7b01e61708db6392d7cf05a4ffec7bc`.
- Tracked run-1 EPF SHA-256:
  `ffd50b306cee13404e3be08d7c4f19e8529e78d86eb9ccf19f0aeb76b3ef5573`.
- Tracked run-2 EPF SHA-256:
  `a9c35c020419b53dcb1e97c354dbce8c40919b902f9186f280296f87d5134b5a`.
- The exact S3 real-TestClient control passed and left zero 1C processes.

## Findings

1. The prior S5 configuration lifecycle was reproduced exactly. The single
   match-all unsafe-action directive was removed only for the bounded run and
   the original content hash, ACL hash and file metadata were restored in a
   `finally` path.
2. The first retained security matrix records an exact S3 exit code of zero.
   Its two instrumented S4 rows exited nonzero with no retained status token
   and list only `IME` and `Static` classes. It does not prove main admission,
   passive UIA, a marker terminal, or an active child at such a terminal.
3. A second fresh matrix varied between `main_not_ready` and the published
   `window_inventory_failed` path while candidate, target, fixture, argv flags
   and configuration lifecycle stayed fixed. The test-only worker hold changed
   timing, but no retained row proves admission. The inherited S4 observer
   boundary is not certified well enough to establish a fixture marker.
4. A later bounded receipt matrix observed an S3-style launch and three S4
   variants reach listener readiness with seven job-owned top-level windows,
   then exit near one second with `0xC0000005` before main admission. Together
   with the other retained failure states, this proves variable pre-admission
   outcomes; it does not identify one terminal state as the root cause.
5. The retained timeline receipts record `ERROR_INVALID_DATA` only on the
   post-exit sample. The earlier matrix separately retains
   `window_inventory_failed` without a structural main receipt. The evidence
   therefore treats the enumeration error as a real fail-closed observation
   and never converts a retry into success, but it does not prove a more
   specific API-level cause.
6. Visual presentation punctuation is not an admissible substitute for the
   exact passive UIA `Name` hash. The replacement must derive and freeze that
   hash from a stabilized tracked-fixture run, then require one match in both
   passive samples.

## Resolved and unresolved hypotheses

- Invalid EPF or empty form is not established by these hidden receipts. The
  tracked managed-form source and prior visible proof remain fixture-
  compatibility context, not hidden-admission evidence.
- An absent main and early `0xC0000005` exit remain observed, unresolved
  possibilities; no retained positive receipt rules either one out.
- Target substitution is ruled out by the exact host, principal, platform,
  target and fixture bindings. An exact baseline S3 exit of zero does not turn
  the separate S3-style diagnostic exit into a positive S4 observation.
- Treating enumeration retry as success is ruled out; every retained S4 state
  remains fail-closed.
- An S7-only defect is not proven. S4-R1 is the smallest bounded place to
  stabilize and structurally recertify the pre-admission observation boundary
  before S7 can resume.

## Cleanup and privacy

Both investigation tasks and stages were removed. Postflight recorded zero
owned tasks, stages and 1C processes; the original configuration content and
ACL hashes, the single match-all directive, boot identity, protected task and
manual visible-proof stage were preserved. Portable evidence retains hashes,
counts, booleans, allowlisted window classes, exit stages and bounded durations
only. It retains no raw UI, captions, screenshots, credentials or protocol
payloads.

## Resume condition

Resume S7 only after the linked S4-R1 card passes, is independently reviewed
and published. Its live floor is an exact S3 pass, two fresh tracked run-1 S4
passes, one uninstrumented S4 confirmation, two run-distinct S5 passes, exact
configuration restoration and zero exact-owned residue. S7 must then rerun its
full final live matrix from the newly published predecessor.
