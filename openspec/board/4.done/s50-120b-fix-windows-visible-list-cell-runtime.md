# S50-120B: Fix Windows visible-list-cell runtime proof

## Status
4.done

## Order Index
120.2

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Blocked card: `openspec/board/3.inprogress/s50-120-bind-remote-ui-actions-to-lifecycle-window.md`
- Investigation: `openspec/board/4.done/s50-120a-investigate-windows-display-type-transport.md`
- Lineage: S50-120 Windows lifecycle-window verification rescue.
- Latest safe published reference: current `origin/main` before S50-120.

## Summary
The source-bound Windows host-agent returns `ok` for
`/uia/visible_list_cells` against the exact owned empty-title target, but it
returns no visible cells for either the original static marker or a native list
marker. Determine whether the Win32/UIA reader or its interactive-session
execution boundary drops the owned fixture descendants, implement the narrow
fix, and rerun the complete S50-120 matrix without weakening target validation.

## Acceptance Criteria
- [x] A Windows-native RED reproducer observes an owned empty-title target whose
  visible native marker is absent from the host-agent result.
- [x] The fixed host-agent returns the marker from that exact lifecycle/client
  target without using a caption, wildcard, generic 1C, or foreground fallback.
- [x] Screenshot, safe-key, `type_text`, click, explicit-selector precedence,
  unrelated-foreground isolation, and weak-target refusal remain green.
- [x] Locked, disconnected, and non-interactive desktop diagnostics still fail
  before the UIA/driver primitive.
- [x] The full source-bound Windows route/session/cleanup matrix is green and
  retains only sanitized evidence under ignored `.runtime/` paths.
- [x] No infobase, business data, native TestClient protocol, or unrelated
  Windows resource is accessed or mutated.

## Evidence Boundary
Retain only sanitized booleans, typed diagnostics, source hashes, test outcomes,
cell-count/marker-presence booleans, and cleanup state. Do not retain raw cells,
screenshots, HWNDs, process identifiers, titles, credentials, response payloads,
or host-agent logs.

## Change Set
- `fix-windows-visible-list-cell-runtime-proof`:
  `openspec/changes/archive/2026-08-01-fix-windows-visible-list-cell-runtime-proof/`

## Change 1: `fix-windows-visible-list-cell-runtime-proof`

### Why
Lifecycle/client resolution reaches the exact empty-title window, but the
Windows UIA descendant reader returns an empty cell set for an owned visible
native marker and blocks the final S50-120 runtime proof.

### Goal
Make visible-list-cell reads observe the owned marker through the exact target
while preserving all lifecycle targeting and typed-session safety guarantees.

### Scope
- Focused Go RED/GREEN coverage for the Windows UIA reader and process-owned
  empty-title target.
- Narrow Windows driver/UIA execution fix or fixture-contract correction,
  selected from retained bounded diagnostics.
- Source-bound Windows proof and exact cleanup.
- No Python MCP behavior, 1C source/metadata, infobase access, protocol capture,
  or business-data mutation.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- `investigate-windows-display-type-transport-proof` (diagnosis and sanitized
  product-boundary handoff).

### Related
- `.runtime/changerail/evidence/investigate-windows-display-type-transport-proof/diagnosis.json`
- `openspec/board/3.inprogress/s50-120-bind-remote-ui-actions-to-lifecycle-window.md`
- `openspec/changes/archive/2026-08-01-fix-windows-visible-list-cell-runtime-proof/`

## Verify
- Windows RED retained: the production reader returned no marker for the owned
  native fixture before the accessible-descendant contract was corrected.
- Windows GREEN retained: the focused regression and the full source-bound
  proof return `VisibleCell` from the exact empty-title target; removing the
  named descendant makes the marker assertion fail again.
- `go test -count=1 ./...` passes; `GOOS=windows GOARCH=amd64 go test -c`
  cross-compiles the exact Windows test payload.
- Authorized-host hashes match the local host-agent and native test binaries.
- The screenshot/key/type/click/visible-cells/override/weak-target/typed-session
  matrix passes; exact task, stage, owned processes, screenshots, token, and
  logs are absent after cleanup.
- `openspec validate fix-windows-visible-list-cell-runtime-proof --strict`,
  `openspec validate --all --strict`, `git diff --check`, Go formatting, and
  the explicit untracked whitespace scan pass.

## Result
Implemented as a fixture-contract correction: an owned WPF `ListBoxItem` with
an explicit UI Automation name now supplies the Windows-native regression and
source-bound runtime proof. The unchanged production reader returns the marker
through the exact empty-title lifecycle target, and the complete route/session
matrix passes without a production driver or predecessor-payload change.

Published reviewed payload as `e337f92`; push status `pending` on `main`/`origin`.

## Archive
- `openspec/changes/archive/2026-08-01-fix-windows-visible-list-cell-runtime-proof/`

## Next
- done

## Log
- 2026-08-01 created from S50-120A after the repaired proof client recovered
  typed `/type` errors but two owned native fixture variants returned no visible
  UIA cells through the exact empty-title target.
- 2026-08-01 ChangeRail fast-forward created the apply-ready proposal, design,
  host-agent security delta, Windows RED/GREEN tasks, bounded evidence matrix,
  and predecessor-payload separation rule.
- 2026-08-01 delivery selected the WPF accessible-descendant fixture contract,
  passed the full source-bound Windows route/session matrix, cleaned the exact
  owned resources, synced the security spec, and completed strict validation.
- 2026-08-01 the publish scan replaced one repository-specific owner path in
  the archived verification matrix with the generic `qa-mcp repository` label.
- 2026-08-01 publish finalized card into `4.done` with commit `e337f92` and push status `pending`.
