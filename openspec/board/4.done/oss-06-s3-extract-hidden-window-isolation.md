# Extract Hidden Window Isolation

## Status
4.done

## Owner
unassigned

## Series
oss-06-s3

## Order Index
405.6

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Add a dormant, read-only S3 primitive that inventories top-level windows on
the exact hidden and operator `Default` Win32 desktops, applies exact
PID/job/class/owner predicates and emits sanitized zero-global-input isolation
receipts without activating a route or sending any UI action.

## Acceptance
- Production additions are at most `300` physical lines across exactly two new
  source files; S1/S2 source remains byte-identical to published `c7a2c20...`.
- Hidden and `Default` inventories retain only HWND, PID, class and owner HWND
  internally; no title, text, control content, geometry, operator application
  identity, input content or raw screenshot is read or retained.
- An exact window is admitted only when one candidate has the expected non-zero
  PID, belongs to the exact lifecycle job, matches the fixed class predicate
  and exact owner HWND, and is present on the requested hidden desktop.
- Missing, duplicate, foreign-PID, outside-job, wrong-class, wrong-owner,
  wrong-desktop and owned-`Default` cases fail closed before any downstream
  observation or action.
- Sanitized receipts expose only bounded counts, hashes and booleans and prove
  zero `SendInput`, `SetCursorPos`, `SetForegroundWindow`, `SwitchDesktop`,
  `mouse_event` and `keybd_event` calls.
- The lifecycle remains dormant: no non-test caller, public API, wire/profile,
  marker/UIA/prompt behavior, addressed key/window message or desktop switch is
  added.
- Clean published-HEAD composition, focused/full Go, vet, Windows test/host
  cross-build, exact-source historical-user synthetic and real-TestClient native cases,
  strict OpenSpec, manifest scope, LOC and diff gates pass before one fresh
  ordinary/high independent review.

## Scope
- Add `hidden_desktop_window_isolation.go` with bounded inventory identity,
  exact predicate/admission and sanitized receipt policy.
- Add `hidden_desktop_window_isolation_windows.go` with read-only
  `OpenDesktopW`, `EnumDesktopWindows`, PID, class and owner enumeration plus
  exact job-membership checks.
- Add portable hostile tests and Windows-native synthetic/real-TestClient
  tests in the two adjacent `_test.go` files.
- Compose only from published S1/S2 and these exact four S3 paths.

## Non-Goals
- No marker, UIA tree, render/capture, chooser, security prompt or form-open
  observation; those belong to S4 or S5.
- No `PostMessage`, `SendMessage`, UIA Invoke/Value/Focus, keyboard, mouse,
  foreground, cursor or desktop-switch action.
- No public tool/route/profile admission, Python change, host wire field,
  arbitrary process execution or stable external-processor flow.
- No S4-S7 implementation or publication in this card.

## Change Set
1. `extract-hidden-window-isolation`

## Depends On
- Published linked replacement
  `openspec/board/4.done/oss-06-s2-r1-eliminate-provisional-job-handle-race.md`.

## Blocks
- `openspec/board/1.backlog/oss-06-s4-extract-direct-execute-observation.md`

## Verification Matrix
| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason | Residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | No 1C layout/source change; hidden top-level window topology is observed only | Exact hidden/default PID/class/owner counts without UI text | `scenario_log`, sanitized `active_window` replacement receipt | `.runtime/changerail/evidence/oss-06-s3-extract-hidden-window-isolation/windows-native.json` | N/A | No managed-form element or visual layout changes | Platform window-class drift is covered by fail-closed native inventory | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Form module or command | No form command or UI action | Hostile zero-action matrix | `scenario_file`, `scenario_log` | `.runtime/changerail/evidence/oss-06-s3-extract-hidden-window-isolation/green-summary.json` | N/A | S3 observes windows and sends no command | Addressed observation starts only in S4 | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Delivery or runtime apply | Exact-source dormant host primitive on trusted Windows host and declared `vanessa_client` | Synthetic owner topology plus exact platform/TestClient hidden lifecycle | `source_preflight`, `qa_testclient_scenario`, `cleanup_evidence` | `.runtime/changerail/evidence/oss-06-s3-extract-hidden-window-isolation/` | required | N/A | Host/platform availability is a typed verification blocker, never replaced by injected proof | `/opt/ai-dev-suite-for-1c/qa-mcp` |

## Verify
- RED hostile tests first for missing/duplicate/foreign/outside-job/wrong-class/
  wrong-owner/wrong-desktop/default-leak and receipt sanitization.
- Exact focused command plus full `go test ./...`, `go vet ./...`, Windows
  test executable and host-agent cross-build.
- Retained clean-composition script from published `HEAD:host-agent` plus only
  the four S3 source/test paths; deterministic `-trimpath` candidate hashes.
- Trusted `HISTORICAL-LAB-HOST\\historical-user` run at the current endpoint: synthetic
  root/owned-popup topology and exact platform `8.3.27.2214` TestClient against
  declared `C:\\1C_BASES\\vanessa_client`, with zero owned `Default` windows,
  zero global input and exact cleanup.
- Preserve listener `18081`, unrelated processes and Docker; no reboot.
- `bin/openspec validate --all --strict`, manifest working-tree/staged scope,
  canonical production LOC `<=300`, forbidden-input source scan and
  `git diff --check`.

## Result
- Delivered and ready for independent review. Portable hostile/receipt/source
  tests, full Go/vet/Windows cross-build and two clean published-HEAD
  compositions pass at `192/300` production lines. Deterministic candidates
  are test `866d40ec...` and host `626e3988...`. One exact interactive historical-user
  run passed both synthetic owner topology and real platform `8.3.27.2214`
  TestClient cases: all hidden windows were exact-job-owned (`3/3` and `7/7`),
  owned `Default` windows and global input/desktop switches were zero, and
  exact cleanup removed task/stage/processes while preserving listener `18081`
  with no Docker mutation or reboot.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `extract-hidden-window-isolation`

### Why
The published S2 lifecycle owns the exact worker/job/listener but has no
reusable proof that all run-owned windows remain on its hidden desktop or that
one exact class/owner surface can be selected without touching operator UI.

### Goal
Publish the smallest dormant read-only window-isolation primitive needed by
later direct-execute observation, with complete hostile and Windows-native
proof and no action authority.

### Scope
- Add the exact four S3 source/test paths.
- Inventory and select only exact hidden-desktop windows.
- Emit sanitized zero-input isolation receipts.
- Keep S4 marker/UIA observation and all action out of scope.

### Acceptance
- All card acceptance criteria pass within the `300`-line production bound.
- Exact-source native evidence binds synthetic and real-TestClient cases to one
  candidate/source lineage and proves exact cleanup.
- A fresh independent ordinary/high review returns `GO` before publication.

### Depends On
- Published S2-R1 commit `c7a2c201b136f36f9f84efd072df65e007344da6`.

### Related
- `openspec/changes/archive/2026-08-30-extract-hidden-window-isolation/`

## Log
- 2026-08-30 S2-R1 published at `c7a2c20...`; operator authorized the next
  stage. S3 moved from backlog to todo and was bounded to four new dormant
  source/test paths with no S4-S7 or public-route scope.
- 2026-08-30 RED established the missing exact admission, hostile, sanitized
  receipt and Windows inventory oracles. The final dormant primitive remains
  caller-free, rejects foreign/ambiguous topology and uses no title, text,
  UIA, input, foreground, addressed-message or desktop-switch authority.
- 2026-08-30 exact Windows run `qa-mcp-oss06-s3-20260830T211244Z` passed
  synthetic and real-TestClient isolation on `HISTORICAL-LAB-HOST\\historical-user`.
  Curated evidence retains only hashes/counts/booleans; exact task/stage were
  removed, 1C processes are zero, listener `18081` is preserved, Docker was
  not mutated and no reboot occurred.
- 2026-08-30 independent review cycle 1 returned `NO-GO` for one blocker: the
  foreign-PID row also left the exact job and did not independently protect PID
  equality. Same-card rescue attempt 1 added an in-job wrong-PID oracle; a
  retained mutation run failed when only `item.PID == pid` was removed. Clean
  candidate `866d40ec...` and exact historical-user run `...213658Z` passed both native
  cases; exact cleanup again left task/stage/1C counts zero and `18081` intact.
- 2026-08-30T21:56:39Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
