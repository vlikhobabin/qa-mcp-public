# Extract Prompt Admission And Action

## Status
3.inprogress

## Owner
qa-mcp

## Series
oss-06-s5

## Order Index
405.8

## OpenSpec Stage
implementation-blocked

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

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
Extract one dormant S5 boundary that admits only the exact lifecycle-local
security prompt and performs one single-use addressed confirmation after fresh
window/control re-admission. It builds only on published S1-R1 through S4 and
does not expose the direct-`/Execute` route publicly.

## Acceptance
- Added production LOC is `<=300` across separate S5 source files; published
  S1-S4 source/tests remain byte-identical to
  `81c60ef0254935a8683d7343016dfc8b88c3911e`.
- One prompt is admitted only when it is new after launch, exact-PID/job/hidden-
  desktop owned, owned by the unchanged S4 main HWND, fixed-class, unique and
  stable for at least three samples.
- Prompt/control topology and the single enabled action control match the
  predeclared structural/action hashes and exact bounded counts without using
  raw UI text, titles, credentials, screenshots or OCR.
- The exact prompt, main window and action control are re-admitted immediately
  before action. Missing, stale, foreign, duplicate, disabled, already-used or
  topology/geometry-drift identity produces zero focus/key/action calls.
- One admitted action may use only hidden-desktop-local UIA focus plus addressed
  key-down/key-up messages to the exact prompt HWND. It never uses chooser,
  `SendInput`, mouse/cursor, global hotkeys, `SetForegroundWindow`,
  `SwitchDesktop` or visible/operator-desktop activation.
- Success requires one prompt transition and one exact S4 marker/topology
  post-state. A persistent/replaced prompt, changed main identity, missing or
  duplicate marker, action retry or non-zero operator-desktop window count
  fails closed.
- The S5 primitive remains dormant with no non-test caller, Python/MCP/public
  route, wire/profile admission, typed cross-language receipt binding or S6/S7
  behavior.
- Hostile RED, focused/full Go, vet, Windows test/host cross-build, two clean
  compositions from published S4, exact-source historical-user prompt-on plus recovery
  rerun, exact cleanup, strict OpenSpec, manifest scope, LOC, predecessor-byte,
  caller/forbidden-action and diff gates pass before one fresh independent
  ordinary/high review.

## Scope
- Add a portable prompt/admission/single-use action policy in a separate S5
  source with adjacent hostile and receipt tests.
- Add one Windows-only exact prompt/control observer and addressed-confirmation
  adapter, with native tests on the hidden worker.
- Reuse published S3/S4 identity and sanitized observation types without
  modifying S1-S4.

## Non-Goals
- No chooser, global input, physical cursor, foreground takeover, desktop
  switch, raw UI retention, screenshot/OCR or business-data mutation.
- No Go/Python receipt or immutable cleanup bridge; S6 owns that boundary.
- No `open_external_processor`, MCP/tool/profile wiring or stable admission;
  S7 owns final integration and certification.
- No roadmap publication, S6/S7 implementation or OSS-07 work.

## Depends On
- Published S4
  `openspec/board/4.done/oss-06-s4-extract-direct-execute-observation.md`

## Blocks
- Replacement S5-R1
  `openspec/board/4.done/oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission.md`

## Change Set
1. `extract-hidden-prompt-admission-action`

## Verify
- RED first for missing/duplicate/old prompt, foreign PID/job/desktop/owner,
  changed main/prompt HWND, unstable samples, topology/action/geometry drift,
  disabled/already-used action and any observer/action call before re-admission.
- Exact focused S5 tests, `go test ./...`, `go vet ./...`, Windows test/host
  cross-builds and two clean compositions from published
  `81c60ef0254935a8683d7343016dfc8b88c3911e` plus only S5 paths.
- Exact-source Windows prompt-on and recovery rerun on
  `HISTORICAL-LAB-HOST\\historical-user`, platform `8.3.27.2214`, target
  `C:\\1C_BASES\\vanessa_client`, proving one addressed confirmation,
  zero global input/desktop switches/operator-desktop windows and exact-owned
  task/stage/PID/job/desktop/TPort/config cleanup while preserving listener
  `18081`, Docker and reboot state.
- Production LOC `<=300`, S1-S4 byte identity, dormant-caller and forbidden-
  action scans, privacy-safe evidence index, strict OpenSpec, manifest
  working-tree/staged scope-check and `git diff --check`.

## Archive
- not started

## Related
- `openspec/changes/extract-hidden-prompt-admission-action/`

## Result
- Portable and Windows-only S5 primitives are implemented in four separate
  files at `250/300` production lines. Hostile RED/GREEN, focused/full Go,
  vet, Windows cross-builds, predecessor/caller/forbidden scans and two clean
  published-S4 compositions pass; the final exact candidates are
  `b0fafc...` (test) and `da5df...` (host).
- Delivery is blocked before spec sync/archive/review: the final exact-source
  native run originally returned `prompt_not_ready`. The authorized bounded
  micro-fix supplied two distinct fresh per-run EPFs and advanced observation
  to a real prompt, but failed closed at `prompt_inventory_not_ready` before
  prompt admission or action.
- Exact micro-fix cleanup restored configuration bytes, ACL and metadata and
  removed only the current-run task/stage/process resources. Docker and boot
  identity were unchanged. Unrelated listener `18081` was present through
  prelaunch but absent after the failed native run, so preservation is not
  proven and the cleanup receipt records `listener_preserved=false`.
- The two original pre-review fix cycles and the one authorized bounded
  micro-fix are exhausted. The remaining target is still two exact-source
  prompt-on/recovery runs with one admitted addressed action and passive S4
  post-state; no review or publication is authorized yet.

## Next
- Do not continue, review, archive or publish this exhausted card.
- Continue only through the review-gated replacement S5-R1; do not resume this
  exhausted lineage.

## Change 1: `extract-hidden-prompt-admission-action`

### Why
Published S4 proves exact action-free main-window/marker/topology observation,
but it cannot admit or confirm a security prompt. S6 cannot bind a trustworthy
receipt until one smaller boundary proves the exact prompt/action identity,
single-use addressed confirmation and post-state without public authority.

### Goal
Publish the smallest dormant S5 primitive that admits one unchanged
lifecycle-local prompt/action identity, performs exactly one addressed
confirmation and proves the exact passive S4 post-state.

### Scope
- Portable fail-closed prompt/action policy and sanitized internal receipt.
- Windows-only structural prompt/control inventory, re-admission and addressed
  confirmation adapter.
- Hostile/mutation, clean-composition and exact Windows prompt/recovery proof.

### Acceptance
- All card acceptance criteria pass within `300` added production lines.
- Any identity/topology/action drift prevents the observer/action callback from
  running; an admitted action is single-use and exact-HWND addressed.
- Exact-source prompt-on and recovery proof completes exact cleanup without
  operator-desktop interference or retained raw UI.

### Depends On
- Published S4 commit
  `81c60ef0254935a8683d7343016dfc8b88c3911e`.

### Related
- `openspec/changes/extract-hidden-prompt-admission-action/`

## Log
- 2026-08-31 fast-forward accepted S5 as one bounded dormant prompt
  admission/action change after published S4. S6/S7, roadmap publication,
  historical combined payload and unrelated `.codex/config.toml` remain
  excluded.
- 2026-08-31 `extract-hidden-prompt-admission-action` reached apply-ready
  artifact state after strict change validation.
- 2026-08-31 implementation and offline verification produced a dormant
  four-file S5 primitive at `250/300` production lines with deterministic
  exact-source candidates `b0fafc...` and `da5df...`.
- 2026-08-31 fix cycle 1 corrected a Windows PowerShell helper-name collision;
  fix cycle 2 added unconditional lifecycle cleanup and typed observer
  diagnostics. The final native run still failed closed at
  `prompt_not_ready`; exact cleanup and configuration restoration passed.
- 2026-08-31 comparison with the prior successful production-route evidence
  found that its two prompt-on runs rebuilt distinct fresh EPFs (`846785...`
  and `f9eea1...`) from candidate `2df4d7...`, while S5 reused candidate
  `2df4d7...` for both runs. This is the leading evidence-backed explanation
  for the absent prompt, but applying it would exceed the current fix budget.
- 2026-08-31 lifecycle supervision authorized one bounded same-card micro-fix.
  A test-only RED/Green change now requires two absolute EPFs with distinct
  paths and SHA-256 content. Clean composition produced deterministic test
  candidate `1899dd...`; production remains `250/300` and host candidate
  remains `da5df...`.
- 2026-08-31 exact historical-user micro-fix built fresh EPFs `c43f70...` and
  `5885a1...`. The prompt appeared, disproving the old `prompt_not_ready`
  condition, but its structural UIA inventory failed closed before admission
  or action. Config restoration and exact current-run cleanup passed; listener
  `18081` drifted from present at prelaunch to absent after the failed run.
- 2026-08-31 operator chose linked S5-R1 replacement: whole-prompt `26/5/0`
  counts and fixed topology hash become diagnostic-only while exact prompt,
  target action, re-admission, single-use and post-state invariants remain.
- 2026-08-31 replacement S5-R1 passed exact-source native proof and reached
  archived, review-gated `3.inprogress`; this exhausted lineage remains
  unpublished.
