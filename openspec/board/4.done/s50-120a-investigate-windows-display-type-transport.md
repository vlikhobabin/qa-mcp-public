# S50-120A: Investigate Windows display type-route transport proof

## Status
4.done

## Order Index
120.1

## Owner
Codex

## OpenSpec Stage
published

## Source
- Blocked card: `openspec/board/3.inprogress/s50-120-bind-remote-ui-actions-to-lifecycle-window.md`
- Lineage: S50-120 Windows lifecycle-window verification rescue.
- Latest safe published reference: current `origin/main` before S50-120.

## Summary
The source-bound Windows lifecycle-window proof reaches the exact empty-title
fixture and passes screenshot, safe-key and unrelated-foreground isolation, but
the PowerShell proof client reports a transport-level failure at `type_text`.
Determine whether the failure is proof-client error parsing, foreground/session
behavior or a host-agent defect, then provide the narrow evidence or follow-up
needed to unblock S50-120 without weakening its verification floor.

## Acceptance Criteria
- [x] Capture the `type_text` HTTP status and bounded structured error code
  without retaining response payloads, window/process identities, screenshots,
  credentials or host-agent logs.
- [x] Distinguish proof-client transport/parsing failure from host-agent
  `foreground-denied`, desktop-session diagnostics and unexpected process exit.
- [x] If the defect is local to the ignored proof harness, repair it and produce
  the complete source-bound five-route, explicit-override, weak-target,
  typed-session and cleanup summary required by S50-120.
- [x] If product code is defective, create a scoped implementation card with
  the exact failing invariant and verification floor before changing S50-120.
- [x] Use only the authorized Windows target, owned fixtures and exact-name
  cleanup; do not access an infobase, mutate business data or capture protocol.

## Evidence Boundary
Retain only sanitized booleans, HTTP status classes, typed error codes, source
hashes, test outcomes and cleanup state under ignored `.runtime/` paths.

## Change Set
- `investigate-windows-display-type-transport-proof`:
  `openspec/changes/archive/2026-08-01-investigate-windows-display-type-transport-proof/`

## Change 1: `investigate-windows-display-type-transport-proof`

### Why
The current proof loses the structured error boundary at `type_text`, so it
cannot show whether the route failed safely or the test client itself failed.

### Goal
Produce a bounded, source-relevant diagnosis and either a green full proof for
S50-120 or a precisely scoped product-fix handoff.

### Scope
- Ignored Windows proof transport/error capture and source-bound rerun.
- Minimal diagnostic instrumentation only; no durable product edit unless a
  later linked implementation card explicitly owns it.
- Exact cleanup and sanitized evidence retention.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- Partial evidence from `s50-120-bind-remote-ui-actions-to-lifecycle-window`.

### Related
- `openspec/board/3.inprogress/s50-120-bind-remote-ui-actions-to-lifecycle-window.md`
- `.runtime/changerail/evidence/bind-remote-ui-actions-to-lifecycle-window/`
- `openspec/changes/archive/2026-08-01-investigate-windows-display-type-transport-proof/`

## Verify
- Deterministic `/type` error control: the legacy client observed HTTP `422`
  but retained only `transport-error`; the bounded client observed the same
  `422/4xx` as `invalid-client-target`, with host-agent and fixture still live.
- Real `type_text`: `200/2xx`, no error code, exact target passed after the
  proof-client repair.
- Source-bound rerun passed screenshot, keys, type, click, explicit override,
  unrelated-foreground isolation, weak-target refusal and all typed-session
  native tests. The visible-cell route returned `ok` for the exact empty-title
  target but no marker for either owned fixture variant, so S50-120B owns the
  residual product boundary.
- All three exact task/stage/process cleanups are green; screenshots, tokens and
  logs were removed.
- Sanitized ignored evidence:
  `.runtime/changerail/evidence/investigate-windows-display-type-transport-proof/{preflight,red-baseline,diagnosis,cleanup,windows-proof-20260801T055447Z}.json`.
- `openspec validate investigate-windows-display-type-transport-proof --strict`:
  passed before archive. Synced capability validation passed; final
  `openspec validate --all --strict`: `21 passed, 0 failed` after archive.
- `git diff --check`, untracked-artifact whitespace scan and sanitized-evidence
  key audit: passed.

## Archive
- `openspec/changes/archive/2026-08-01-investigate-windows-display-type-transport-proof/`

## Result
The `type_text` blocker was a proof-client parsing defect, not a host-agent
exit or desktop-session failure. The repaired client recovered bounded typed
errors and the real type route passed. The complete rerun then isolated a
separate Windows visible-list runtime boundary and created S50-120B with the
exact invariant and unchanged verification floor.

Independent review cycle 1 returned `GO` with no findings. The reviewed payload
commit is `476131c`; card-only finalization targets `origin/main`, with the final
push result retained in the ignored delivery manifest.

## Next
- `$changerail-deliver openspec/board/2.todo/s50-120b-fix-windows-visible-list-cell-runtime.md`

## Log
- 2026-08-01 created automatically after S50-120 exhausted its pre-review fix
  budget plus one bounded same-card continuation at the Windows `type_text`
  transport boundary.
- 2026-08-01 ChangeRail fast-forward created the apply-ready proposal, design,
  diagnostic capability spec, and bounded Windows investigation tasks.
- 2026-08-01 ChangeRail delivery started the bounded ignored Windows proof
  investigation; product-code paths remain owned by S50-120 and excluded.
- 2026-08-01 the deterministic `/type` control proved legacy proof-client error
  parsing lost a typed `422` response; the bounded client recovered it and the
  real type route passed.
- 2026-08-01 the full rerun isolated an empty Windows UIA visible-cell result on
  the exact target across two owned fixtures, completed exact cleanup, and
  created the scoped S50-120B implementation handoff.
- 2026-08-01 ChangeRail synced the diagnostic capability, archived the completed
  investigation change, and left the card in review-gated `3.inprogress`.
- 2026-08-01 independent review cycle 1 returned `GO` with no findings or
  unbacked mandatory claims.
- 2026-08-01 ChangeRail created reviewed payload commit `476131c` and finalized
  the card for publication to `origin/main`.
