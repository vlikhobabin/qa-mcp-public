# Stabilize External Processor Open Flow

## Status
2.todo

## Owner
qa-mcp

## Series
oss-06

## Order Index
405

## OpenSpec Stage
parent / final child certification active

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
- Sanitized UI smoke of a synthetic external processor on a Linux TestClient.

## Problem
`open_external_processor` depends on a fixed application-menu coordinate and
OCR of menu labels. In field validation it first opened the wrong surface, then
typed into application search instead of the native file-open dialog. One
attempt timed out, exposed live directory text in a screenshot and left an
additional client window that had to be stopped manually.

The delivery incorrectly fell back to direct Xvfb input against an alternate
file infobase. That proved the form could open but bypassed the intended qa-mcp
workflow, did not exercise the user file-selection flow and did not prove
behavior in the connected project's declared base.

## Goal
Make external processor opening deterministic, owned, privacy-safe and
self-cleaning on the supported TestClient contour while honoring the declared
project's local evidence-retention policy.

## Acceptance
- The tool targets an explicitly owned TestClient and verifies foreground
  window identity before sending any input.
- The owned TestClient is bound to the project target id and fingerprint from
  the shared descriptor; a call cannot supply or switch the connection.
- Menu/file-open navigation uses an addressed native route or verified visual
  state rather than a hard-coded coordinate alone.
- Before typing a path, the tool proves that the native file chooser and its
  location field are active; application search or another input surface fails
  closed without typing.
- The operation recognizes and safely handles only an external-processing
  security prompt owned by the launched flow.
- Results expose structured stages such as `menu_not_found`,
  `file_dialog_not_open`, `security_prompt`, `form_opened`, `caption_mismatch`
  and `cleanup_failed`.
- The ignored provider/project profile selects an evidence policy, at minimum
  `sanitized` or `full_local`; model tool input cannot weaken or override it and
  cannot select an arbitrary evidence root.
- `sanitized` remains the portable/default product policy. `full_local` is an
  explicit operator policy for a declared non-production target and retains raw
  screenshots, OCR/UI text, tool traces and failure state, including business
  data, under an allowlisted Git-ignored local runtime root.
- Every retained artifact reports its path, hash, sensitivity classification,
  target id/fingerprint, operation id and lifecycle state in a local manifest.
  Credentials and authentication tokens are redacted under both policies.
- Active `full_local` evidence is not deleted merely because a failed UI route
  exposed business data. Cleanup remains an explicit terminal retention action;
  product-facing results and fixtures remain sanitized.
- Timeout and failure close owned dialogs/client processes and leave no owned
  session or orphan X-display process; they neither create nor switch an
  infobase.
- A synthetic EPF and preconfigured synthetic project target prove positive
  open, wrong-menu, missing-file, security-prompt and timeout cleanup cases on
  8.3.27.2214.
- Missing or mismatched declared target fails before UI input, and no failure
  path launches another client, creates a database or falls back to direct Xvfb
  automation outside qa-mcp.

## Non-Goals
- Opening an EPF in an arbitrary already-running business client.
- Generic unverified mouse automation.
- Replacing protocol-level form assertions after the form is open.

## Dependencies
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`
- `openspec/board/4.done/oss-05-extract-independent-open-windows-host-bridge.md`

## Release Gate
- Until this card is delivered with target-bound Linux/Windows recovery proof,
  `open_external_processor` must be absent from the stable standalone profile.
- That explicit omission allows source, release-candidate and stable releases
  of all other qualified standalone capabilities.

## Child Delivery Snapshot

| Order | Child | State | Outcome |
| ---: | --- | --- | --- |
| 405.2 | I2 investigation decision | `4.done` | published bounded hidden direct-execute design |
| 405.3 | A2 authorization | `4.done` | published `<=500` final-integration authority |
| 405.41 | S1-R1 process foundation | `4.done` | published replacement for exhausted S1 lineage |
| 405.51 | S2-R1 lifecycle race replacement | `4.done` | published |
| 405.6 | S3 hidden-window isolation | `4.done` | published |
| 405.7 | S4 direct-execute observation | `4.done` | published |
| 405.81 | S5-R1 addressed prompt admission | `4.done` | published replacement for exhausted S5 lineage |
| 405.9 | S6 typed receipt foundation | `4.done` | published |
| 405.10 | S7 public-route admission | `2.todo` | apply-ready but incomplete; I13 and S4-R1 prerequisites remain open |
| 405.101 | S7-I1 main-window absence investigation | `4.done` | published bounded S4-R1 replacement decision |
| 405.102 | S4-R1 observation lifecycle stabilization | `2.todo` | incomplete; published I11 exists but required certification remains open |
| 405.103 | S4-R2 pre-receipt exit investigation | `4.done` | published bounded pre-first-checkpoint exit decision |
| 405.10196 | I13 published-I11 certification | `3.inprogress` | active, unarchived and uncertified after fail-closed S4 stop |
| 405.10197 | I14 topology investigation | `4.done` | published `NOT-VERIFIABLE` decision; non-certifying |
| 405.10198 | I15 Session-1 admission retry | `4.done` | published `NOT-VERIFIABLE`; no receipt and zero candidate invocation |
| 405.10199 | I16 stable-profile omission | `3.inprogress` | evidence/docs/spec/board decision; no retry or source deletion |

The original S1 and S5 cards remain immutable exhausted `NO-GO` lineage and
are not publication or continuation targets.

## Change Set
- none on this parent card; each bounded child owns its own Change Set,
  verification, review and publication.
- current release decision: `record-stable-profile-omission-after-i15`

## Related
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/protocol/native_xtest.py`
- TestClient lifecycle and display backend contracts
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Verify
- Hermetic display-backend tests for every structured stage.
- Linux lab smoke with a synthetic EPF and owned TestClient.
- Process/lock cleanup assertions and `sanitized`/`full_local` evidence-policy
  tests, including fail-closed caller override, manifest provenance and
  credential redaction.
- Full `qa-mcp` suite and strict OpenSpec validation.

## Result
The bounded OSS-06 investigation, authorization and S1-R1 through S6
foundations are published. S7 has composed them into the public route and has
passed offline scope, LOC, predecessor, Go and Python gates. The former fixture
blocker is repaired: two tracked EPFs include complete Designer XML/BSL sources
and non-empty managed forms, and visible Windows `8.3.27.2214` `/Execute` proof
confirmed the run-1 title, marker field, value and read-only state. This proof
does not replace the pending hidden S4/S5 observer, prompt/recovery,
Python-to-MCP or typed-cleanup matrix. S7 review and publication have not
started.
Published S7-I1 authorized the bounded S4-R1 lifecycle replacement. S4-R1 now
passes its clean offline floor and exact S3 control, but the first passive
run-1 S4 marker-derivation row exits nonzero before a positive receipt. It is
safely blocked. Linked investigation `405.103` classified two passive runs as
`process_exit/candidate_exited_without_checkpoint` before listener readiness,
with zero action. The operator-approved immutable receipt proves exact config
bytes, ACL, all four metadata fields and owned cleanup. The bounded decision
targets first-checkpoint creation and does not authorize S4-R1 or S7 resume.
Published I15 then used its one authorized original-route canary, received no
typed Session-1 receipt and invoked no candidate. I16 satisfies this parent's
release gate by omitting `open_external_processor` from the stable standalone
profile/public support matrix. The dormant implementation and all foundations
remain, while I13, S4-R1 and S7 remain incomplete and uncertified.

## Next
- I16 omission is published at `10598ef`; OSS-07-R1 public readiness is
  published at `8e94a21`. Their publication does not certify I13/S4-R1/S7.
- Retain this parent as a release-gate record: omission satisfies that fork,
  while runtime qualification remains incomplete. Any future qualification
  needs a separately reviewed successor and new explicit runtime authority.
- The next release-sequence planning story is OSS-08. See the
  [board inventory](../../../docs/development/board-inventory-2026-09-05.md).

## Log
- 2026-08-20T17:30:00Z created from sanitized field-validation evidence.
- 2026-08-21: replaced the disposable-infobase fallback with the declared
  project-target dependency and fail-closed no-substitution acceptance.
- 2026-08-21: added an operator-controlled `full_local` evidence policy for
  complete local diagnostics on an approved test target without permitting
  customer data in product commits or portable evidence.
- 2026-08-24 assigned as roadmap card 405; it no longer blocks stable release
  when the unsupported tool is explicitly omitted from the standalone profile.
- 2026-08-27 moved to `2.todo` as planning-ready after OSS-04 publication and
  confirmation that OSS-05 is apply-ready. No fast-forward or implementation
  work was started in the OSS-04F session.
- 2026-08-27 OSS-05 published the independent open Windows host bridge; OSS-06
  is now unblocked for a separate fast-forward command. No OSS-06 artifacts or
  implementation were started.
- 2026-09-01 parent refreshed after the bounded I2/A2 and S1-R1 through S6
  sequence published and S7 reached final certification. The comment-only
  temporary EPFs were replaced by tracked binaries plus full form sources;
  rebuild/reverse-dump and visible Windows proof now establish real managed
  forms. Hidden task-5 certification, fresh critical review and publication
  remain the only current OSS-06 delivery path.
- 2026-09-01 S7 diagnostics localized the unresolved failure after real S3 and
  before S4 main-window admission. Planned linked investigation `405.101`
  because the current S7 authorization forbids changing published S4 bytes.
- 2026-09-01 S7-I1 published the bounded S4-R1 decision. S4-R1 passed offline
  composition and exact S3, then stopped safely when passive run-1 S4 exited
  before a positive marker receipt. Planned linked typed-diagnostic
  investigation `405.103`; S4-R1 and S7 remain blocked and no S5 action or
  OSS-07 work is admitted.
- 2026-09-01 S4-R2 offline floors and exact S3 passed; two passive rows agreed
  on a pre-checkpoint process exit with zero action. Exact task/stage/process
  cleanup and config bytes/ACL passed, but missing pre-run metadata timestamps
  forced `NOT-VERIFIABLE`; no review, archive, commit or push followed.
- 2026-09-01 S4-R2 supervised resume accepted the completed immutable receipt
  without a live rerun. Exact metadata cleanup is proven; the curated decision
  limits the finding to a pre-first-checkpoint candidate exit and leaves S4-R1,
  S7 and downstream cards stopped pending separate authorization.
- 2026-09-02 published I15 admitted no typed Session-1 receipt and invoked no
  candidate. I16 records the stable-profile/public-support omission without
  deleting dormant source or changing I13/S4-R1/S7 completion state; OSS-07 is
  next as a separate unplanned backlog card.
