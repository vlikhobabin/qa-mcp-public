# Extract Direct-Execute Observation

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4

## Order Index
405.7

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
Add a dormant, observation-only S4 primitive for an exact hidden direct-
`/Execute` lifecycle. It binds the published S3 identity types and admission
predicates to one main window, compares one UIA marker only by a caller-supplied
SHA-256, inventories bounded structural UIA identity and returns sanitized
receipts without any UI action.

## Acceptance
- Production additions are at most `300` physical lines across separate S4
  source files; published S1-S3 source remains byte-identical to
  `46287cba55d2e4cbb84e9367ed330d2dfd55dbda`.
- One exact main window is admitted only by current hidden desktop, lifecycle
  PID/job, fixed class/owner identity and exact unchanged HWND; missing,
  duplicate, foreign or changed identity fails closed.
- The expected marker is supplied only as a lowercase SHA-256. Observation
  reads UIA names only in memory, compares their hashes and retains neither raw
  names nor any other UI text; missing or duplicate matches are refused.
- The UIA inventory is bounded and structural: control-type, class,
  automation-id and supported-pattern hashes/counts only. Foreign PID,
  malformed hashes, overflow or ambiguous/changed topology is refused.
- Sanitized receipts contain only typed outcomes, bounded counts, booleans and
  hashes; raw UI text, titles, credentials, connection strings, geometry and
  screenshots are never retained.
- Every hostile and native outcome proves action count `0`; S4 contains no
  `SendInput`, mouse/cursor, foreground/desktop switch, global key, chooser,
  UIA Invoke/Value/Focus or addressed window/key action primitive.
- The primitive remains dormant: no non-test caller, public API, wire/profile,
  Python/MCP integration, prompt action or S5-S7 behavior is added.
- Focused/full Go, vet, Windows test/host cross-build, clean published-HEAD
  composition, exact-source historical-user direct-`/Execute` observation, strict
  OpenSpec, manifest scope, LOC, forbidden-action and diff gates pass before
  one fresh ordinary/high independent review.

## Scope
- Add one portable S4 policy/receipt source and one Windows-only passive UIA
  inventory source, with adjacent portable and Windows-native tests.
- Reuse published S3 identity/job/desktop admission without modifying S1-S3.
- Extract only the passive main-window/marker/topology slice from the dirty
  combined investigation candidate; do not stage that combined file.

## Non-Goals
- No prompt admission or confirmation; S5 owns that action boundary.
- No typed Go/Python receipt bridge, public route or stable admission; S6/S7
  own those boundaries.
- No chooser, raw text/title/screenshot retention, capture, global input,
  foreground takeover, desktop switching or UIA/action pattern invocation.

## Depends On
- `openspec/board/4.done/oss-06-s3-extract-hidden-window-isolation.md`

## Blocks
- `openspec/board/1.backlog/oss-06-s5-extract-prompt-admission-action.md`

## Change Set
1. `extract-hidden-direct-execute-observation`

## Verify
- Hostile RED first for missing/duplicate marker, foreign PID/job/desktop/window,
  changed main identity, ambiguous UIA topology, credential/raw-text leakage
  and non-zero action count; retain exact RED commands and unsafe mapping.
- Exact focused S4 tests, `go test ./...`, `go vet ./...`, Windows test and host
  cross-builds, clean composition from published HEAD plus only S4 paths.
- Exact-source Windows observation on `HISTORICAL-LAB-HOST\\historical-user`, platform
  `8.3.27.2214`, target `C:\\1C_BASES\\vanessa_client`, with exact-owned
  task/stage/PID/job/desktop/TPort cleanup, listener `18081` preservation, no
  Docker mutation and no reboot.
- Production LOC `<=300`, S1-S3 byte identity, caller and forbidden-action
  scans, `bin/openspec validate --all --strict`, manifest working-tree/staged
  scope-check and `git diff --check`.

## Result
- Delivered and ready for independent review. Hostile compile RED and six
  mutation-sensitive RED oracles cover exact main identity, foreign PID,
  marker cardinality, ambiguous/changed topology and action/privacy invariants.
- Focused/full Go, vet, Windows cross-build and two clean compositions from
  published `46287c...` pass at `227/300` production lines. Rescue-1
  deterministic candidates are test `1baa8f6f...` and host `e8f32b91...`.
- The exact-source worker-local historical-user proof passed on platform `8.3.27.2214`:
  marker count `1`, UIA control count `85`, stable topology, action/input/
  desktop-switch counts `0`, no owned `Default` windows and no retained raw UI.
  An earlier controller-side diagnostic failed action-free; all its exact-owned
  resources were removed before the final worker-local GREEN run.
- Exact cleanup removed only the current-run task/stage/process/job/desktop/
  TPort resources; listener `18081` and Docker state were preserved and no
  reboot occurred. S1-S3 remain byte-identical and S4 has no non-test caller.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `extract-hidden-direct-execute-observation`

### Why
Published S3 proves exact window isolation but deliberately stops before
marker or UIA observation. S5 cannot safely address a prompt until a smaller
primitive proves one unchanged direct-execute main window and one sanitized,
unambiguous structural post-state without action authority.

### Goal
Publish the smallest dormant observation-only boundary that binds exact main
window identity, caller-supplied marker hash and bounded UIA topology while
failing closed with action count zero.

### Scope
- Add separate portable/Windows S4 source and adjacent tests only.
- Add hostile RED, exact Windows observation and sanitized evidence.
- Sync/archive one new capability without changing public behavior.

### Acceptance
- All card acceptance criteria pass within `300` added production lines.
- Exact-source Windows proof observes the direct-`/Execute` marker/topology and
  completes exact cleanup without UI action or operator-desktop interference.
- One fresh independent ordinary/high review returns `GO` before publication.

### Depends On
- Published S3 commit `46287cba55d2e4cbb84e9367ed330d2dfd55dbda`.

### Related
- `openspec/changes/extract-hidden-direct-execute-observation/`

## Log
- 2026-08-31 fast-forward accepted S4 as one bounded dormant observation
  change after published S3. S5-S7, the dirty combined candidate and unrelated
  `.codex/config.toml` remain excluded.
- 2026-08-31 implementation synced and archived
  `extract-hidden-direct-execute-observation`; exact-source Windows observation
  and exact-owned cleanup passed with zero UI actions.
- 2026-08-31 review cycle 1 returned `NO-GO`: second exact-window admission
  occurred after the second passive UIA traversal. Bounded rescue 1 retained a
  behavior-sensitive RED, moved re-admission before the observer callback and
  proved changed identity leaves the callback count at zero. Full offline and
  exact-source Windows observation/cleanup gates then passed again.
- 2026-08-31T06:30:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
