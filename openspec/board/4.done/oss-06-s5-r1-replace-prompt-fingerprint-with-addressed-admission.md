# Replace Prompt Fingerprint With Minimal Addressed Admission

## Status
4.done

## Owner
unassigned

## Series
oss-06-s5-r1

## Order Index
405.81

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Replaces
- Exhausted unpublished S5
  `openspec/board/3.inprogress/oss-06-s5-extract-prompt-admission-action.md`.

## Source Lineage
- Latest published baseline:
  `81c60ef0254935a8683d7343016dfc8b88c3911e`.
- The exhausted S5 four-file candidate, its ignored evidence and its active
  OpenSpec change are input evidence only. They MUST NOT be published as the
  successful S5 result or used to bypass this replacement's RED/native gates.
- Fresh per-run EPFs first exposed `prompt_inventory_not_ready`; the bounded
  observer repair now admits the exact unique Button while failing closed on
  unreadable Button rows and ignoring unreadable unrelated UIA rows.
- Exact S5 cleanup restored configuration and removed current-run resources;
  Docker and boot identity were unchanged. Listener `18081` independently
  drifted during proof and is retained only as non-gating diagnostics.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Replace S5's brittle whole-prompt UIA fingerprint with the smallest dormant
addressed admission boundary: exact prompt ownership, one unique stable target
action, immediate re-admission, a single addressed confirmation and exact S4
post-state. Unrelated prompt controls remain bounded diagnostics and do not
decide admission.

## Acceptance
- Added production LOC remains `<=300` across separate S5-R1 files; published
  S1-S4 bytes remain identical to published baseline `81c60ef...`.
- One prompt is admitted only when it is new, unique, exact-PID/job/hidden-
  desktop/main-owner bound and unchanged across two consecutive bounded
  observations.
- One action is admitted only when its exact PID, control type, predeclared
  action path, enabled/visible/invokable state, relative action rank and
  non-empty root/action geometry identity are unique and unchanged immediately
  before action.
- Total UIA control count, total Invoke/Value counts and a hash of the complete
  prompt topology are retained only as sanitized diagnostics. No exact
  `26/5/0` totals or fixed whole-prompt pattern hash may gate admission.
- Missing, stale, foreign, duplicate, disabled or changed prompt/action
  identity produces zero focus/key/action calls. Changes to unrelated controls
  alone do not reject an otherwise exact action identity.
- One admitted action uses only hidden-desktop-local focus and one addressed
  Return key-down/key-up pair to the exact prompt HWND, with no retry.
- Success requires prompt closure, no replacement prompt, unchanged exact main
  identity and the exact passive S4 marker/topology post-state with zero
  operator-desktop windows.
- The primitive stays dormant: no non-test caller, Python/MCP/public/profile
  admission, S6 receipt binding or S7 integration.
- Exact-source Windows prompt-on and recovery rerun use two distinct fresh
  per-run EPFs and prove one action per run plus exact-owned cleanup.
- Listener `18081` is diagnostic-only unrelated inventory. S5 never connects
  to, restarts, stops or reconfigures it; its presence, absence, ownership or
  independent drift does not gate certification.

## Scope
- Replace only the portable S5 policy, Windows observer/action adapter and
  adjacent tests in the four isolated S5 paths.
- Add bounded typed diagnostics sufficient to distinguish UIA command failure,
  observed row count, foreign/malformed rows, action-match count and hash
  validity without retaining raw UI.
- Reuse published S3/S4 identities and the already proven fresh-EPF harness;
  keep S1-S4 byte-identical.

## Non-Goals
- No chooser, `SendInput`, mouse/cursor, global hotkeys, foreground takeover,
  desktop switching, OCR, screenshots or raw UI retention.
- No weakening of prompt ownership, exact target-action identity, single-use
  action, re-admission, passive post-state or cleanup invariants.
- No Python/MCP/public route, wire/profile admission, S6/S7 implementation,
  roadmap publication or OSS-07 work.
- No connection, restart, stop, repair or reconfiguration of listener `18081`.

## Depends On
- Published S4
  `openspec/board/4.done/oss-06-s4-extract-direct-execute-observation.md`.
- Exhausted unpublished S5 lineage and its sanitized native evidence.

## Blocks
- `openspec/board/1.backlog/oss-06-s6-bind-direct-execute-receipt-foundation.md`

## Change Set
1. `replace-hidden-prompt-fingerprint-with-addressed-admission`

## Verify
- Hostile RED first for irrelevant-control count/pattern drift that the old
  implementation rejects but the minimal model must admit without weakening
  exact action identity.
- Hostile RED for missing/old/duplicate/foreign prompt, duplicate/foreign/
  disabled/changed action, pre-action identity drift and used ledger, proving
  zero action calls on every rejection.
- Focused/full Go, vet, Windows test/host cross-build and two clean compositions
  from published `81c60ef...` plus only exact S5-R1 paths.
- LOC, S1-S4 byte identity, dormant-caller, forbidden-action, privacy, strict
  OpenSpec, manifest scope and `git diff --check` gates.
- Read-only diagnostic listener inventory, then exact-source historical-user
  prompt-on and recovery runs with fresh per-run EPFs, exact S4 post-state and
  exact current-run cleanup.
- One fresh independent ordinary/high `GO` before scoped publication.

## Archive
- `openspec/changes/archive/2026-08-31-replace-hidden-prompt-fingerprint-with-addressed-admission/`

## Related
- `openspec/changes/replace-hidden-prompt-fingerprint-with-addressed-admission/`
- `openspec/changes/extract-hidden-prompt-admission-action/`

## Result
- Portable minimal-addressed admission and the bounded Windows observer/action
  are implemented in the four isolated S5-R1 paths. Focused/full Go, vet,
  Windows cross-build, deterministic clean composition, `279/300` LOC,
  predecessor-byte, dormant-caller and forbidden-action gates pass.
- Exact-source historical-user proof passed with two new distinct comment-only EPFs,
  two admitted confirmations, four addressed key messages, prompt closure,
  exact passive S4 post-state, zero operator-desktop windows, zero global input
  and zero desktop switches. No raw UI, credentials or screenshots were
  retained.
- Security configuration bytes, ACL and metadata were restored exactly. The
  exact task/stage/process/job/desktop/TPort lifecycle was cleaned to zero;
  Docker and boot identity were unchanged. Listener `18081` drifted `1 -> 0`
  independently and did not gate or receive any S5 operation.
- The single capability spec is synced and the single change is archived.
  Independent review cycle 1 returned `NO-GO` only for a confounded historical
  fingerprint RED and two stale listener-ownership sentences.
- Bounded rescue 1 now isolates the RED with the legacy three-sample condition
  satisfied, makes archived listener semantics coherent and passes a new exact-
  source native proof. Its deterministic candidate hashes are `688b592f...`
  (test) and `6fc26cfd...` (host). Fresh independent review cycle 2 returned
  `GO` with 10/10 acceptance, zero findings and zero unbacked claims.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `replace-hidden-prompt-fingerprint-with-addressed-admission`

### Why
The exhausted S5 proved prompt appearance with fresh EPFs but overfit admission
to one complete UIA inventory. That fingerprint rejects harmless drift in
unrelated controls before it can evaluate the exact target action.

### Goal
Deliver the minimum fail-closed addressed prompt admission required by S6:
exact lifecycle prompt, exact unique action, immediate re-admission, one
addressed confirmation and exact passive post-state.

### Scope
- Rewrite the isolated S5 policy/adapter and tests from published S4 plus the
  explicitly admitted safe portions of the four-file candidate.
- Make whole-inventory totals diagnostic-only while preserving exact target
  action identity, single-use ordering and privacy-safe receipts.
- Prove two fresh prompt/recovery runs and separate listener-contour integrity.

### Acceptance
- Every card criterion and delta requirement passes within `300` production
  lines and without changing any published predecessor.
- Harmless unrelated-control drift is admitted; every prompt/action identity
  or ordering drift fails before action.
- Exact-source native and cleanup evidence pass before independent review.

### Depends On
- Published S4 and the exhausted S5 evidence lineage.

### Related
- `openspec/changes/replace-hidden-prompt-fingerprint-with-addressed-admission/`

## Log
- 2026-08-31 created as the bounded lifecycle replacement after exhausted S5
  and one authorized micro-fix stopped at `prompt_inventory_not_ready` before
  any action.
- 2026-08-31 operator selected minimal addressed admission instead of full
  prompt fingerprinting or prompt-off omission.
- 2026-08-31 implementation and offline gates passed, then the required
  read-only Windows preflight stopped on `runtime_contour_drift` because
  listener `18081` was absent and its owner/lifecycle could not be identified.
- 2026-08-31 operator-authorized bounded re-scope made unrelated listener
  `18081` diagnostic-only after lineage/source inspection proved S1-S5 only
  count it before/after cleanup and never connect to or operate on it.
- 2026-08-31 exact-source native proof passed two fresh per-run EPFs with two
  confirmations, four addressed messages, exact S4 post-state and exact-owned
  cleanup; listener `18081` independently drifted without gating the run.
- 2026-08-31 synced only `qa-mcp-minimal-addressed-prompt-admission`, archived
  only the S5-R1 change and moved the card to review-gated `3.inprogress`.
- 2026-08-31 independent review cycle 1 returned `NO-GO`: the retained RED hit
  the old three-sample gate before whole fingerprinting, and two archived
  listener sentences contradicted the authorized diagnostic-only re-scope.
- 2026-08-31 bounded rescue 1 added a fingerprint-specific legacy-mutation RED
  with three samples, corrected only those archived sentences and passed full
  offline plus new exact-source historical-user proof and exact cleanup.
- 2026-08-31 fresh independent review cycle 2 returned `GO`: 10/10 acceptance,
  zero findings and zero unbacked claims; S6 remained unstarted.
- 2026-08-31T13:45:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
