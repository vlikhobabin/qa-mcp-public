# read_list_grid positive read blocked on Бухгалтерия 3.0 — config-matched capture refresh (epic 111 item 4)

## Status
4.done

## Owner
/opt/ai-dev-suite-for-1c/qa-mcp

## OpenSpec Stage
archived; external review passed; published. This is epic 111 **item 4** ("reduce fragility to the
platform-protocol version" + refresh-capture procedure), scoped to the concrete
[redacted third-party configuration] blocker. Runtime positive-read proof is recorded as a provider gap
while the real Windows .205 / [redacted third-party configuration] host is unavailable.

## Change Set
- `read-list-grid-positive-read-capture-refresh` →
  `openspec/changes/archive/2026-07-08-read-list-grid-positive-read-capture-refresh/`

## Verify
- `$opsx-ff`: `openspec validate read-list-grid-positive-read-capture-refresh --strict`
  and scoped `git diff --check` passed while preparing artifacts.
- `$opsx-do`: focused RED/GREEN pytest for capture metadata, manager-handshake
  drift, and list-table diagnostic propagation passed.
- `$opsx-do`: broader affected pytest for protocol/session/list-read surfaces
  passed.
- `$opsx-do`: `uv run python -m qa_mcp.regression.versioning` passed without
  live [redacted third-party configuration] claims.
- `$opsx-do`: matrix preflight and archive-gate checks passed with one explicit
  qa-mcp provider gap for the unavailable [redacted third-party configuration] positive-read proof.
- `$opsx-do`: full `uv run --with pytest --with pyyaml pytest` passed with
  787 collected tests.
- `$opsx-do`: suite source-of-truth drift fallback check passed with
  0 findings, and smoke pytest passed with 3 selected tests.
- `$opsx-do`: `openspec validate qa-mcp-protocol-lab --strict`,
  `openspec validate --all`, and `git diff --check` passed after spec sync.

## Archive
- `openspec/changes/archive/2026-07-08-read-list-grid-positive-read-capture-refresh/`

## Result
Implemented the offline-testable protocol-lab scope: sanitized capture metadata
and selection, config-tagged bundled capture sidecars, a Linux-native refresh
metadata helper, refresh-capture runbook updates, and a specific
`manager-handshake-moved` diagnostic for the manager ACK/GUID drift case. The
real [redacted third-party configuration] `read_list_grid` positive read was not run in this session and
is recorded as a qa-mcp provider gap at
`.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md`.
Published by the scoped `$opsx-pub` commit; ignored runtime review and manifest
files were left out of git.

## Next
- none for this OPSX card. Complete the runtime checkpoint on the real Windows
  .205 / [redacted third-party configuration] host when it becomes available.

## Source
- 2026-07-08 .205 [redacted third-party configuration] runtime acceptance (see
  `docs/qa-mcp-connection-issues-2.md` → Resolution). The card
  `read-list-grid-fail-loud-and-remote-window-discovery` P0 fail-loud guarantee
  was proven (read_list_grid never returns a fabricated `row_count:0`), but the
  **positive read** of a real list could not be completed on this config.

## Problem
With a healthy, persistent client on [redacted third-party configuration] (interactive-launched, login not
stuck, `testclient_smoke` green, TPort on `0.0.0.0`, `V8TopLevelFrameSDI` window
up), `read_list_grid` on `e1cib/list/Справочник.Валюты` fails **deterministically
(4/4)** at the session-manager handshake:

```
ValueError: client ACK GUID not found in response after manager frame 3
→ ConnectionResetError: [Errno 104] Connection reset by peer
```

It correctly fails loud (`ok:false`, `list-table-unresolved`,
`available_tables:[]`) — never a fabricated empty read — but the live form
descriptor never resolves, so the visible row is not returned.

Root cause: the capture-replay **session-bootstrap frames** were derived on
`demo10413` (a different configuration). The manager-frame ACK/GUID handshake
does not line up on **Бухгалтерия предприятия 3.0** (platform 8.3.27.2130) when
driven **over the LAN**. The earlier connection-issues run resolved the
descriptor via the on-host container (localhost); this config + LAN transport
exposes the capture's version/config fragility.

## Scope
Per epic 111 item 4, applied to this concrete blocker:
1. **Version/config-tag captures** — record which platform build and
   configuration (e.g. `8.3.27.2130` / `Бухгалтерия 3.0`) each capture was
   recorded on, in the capture/evidence metadata.
2. **Refresh-capture procedure** — a documented runbook to re-record the
   irreducible session-bootstrap + list-open/read templates on a target build +
   config, and select the config-matched capture at read time.
3. **Handshake drift detector** — a fast preflight that flags specifically that
   the live **manager handshake** (ACK/GUID after the session-bootstrap frames)
   no longer matches the captured one, so the failure is diagnosed as "protocol
   moved / capture mismatch", not generic breakage.
4. Prove `read_list_grid` positive read of `Справочник.Валюты` on [redacted third-party configuration]
   returns the visible row(s) with a config-matched capture.

## Acceptance
- `read_list_grid` on `Справочник.Валюты` ([redacted third-party configuration], 8.3.27.2130,
  Бухгалтерия 3.0) returns the visible row(s) using a config-matched capture.
- Captures carry a platform-build + configuration stamp.
- The drift detector fails loudly and specifically ("manager handshake moved")
  when the live handshake diverges from the captured one.
- Regression: demo10413 and other proven configs still read correctly.

## Change 1: `read-list-grid-positive-read-capture-refresh`

### Why
The list-read replay is fragile to the platform build + configuration it was
captured on; a config-matched capture and a specific drift signal are needed to
read real customer configs (Бухгалтерия 3.0) reliably.

### Goal
Version/config-tag captures, document + tool a refresh-capture procedure, add a
manager-handshake drift detector, and prove the [redacted third-party configuration] positive read.

### Scope
- Capture metadata + selection by build/config.
- Refresh-capture runbook/tooling.
- Handshake drift preflight in the protocol layer.
- Runtime proof on [redacted third-party configuration] (record a provider gap when the host is
  unavailable).

### Acceptance
- As in the card Acceptance.

### Depends On
- `host-agent-launched-testclient-persistence` (a persistent client is needed to
  drive the read) OR an interactive-launched client as the runtime harness.

### Related
- `docs/qa-mcp-connection-issues-2.md` (Resolution), epic 111 item 4,
  `read-list-grid-fail-loud-and-remote-window-discovery` (archived).
- `openspec/changes/archive/2026-07-08-read-list-grid-positive-read-capture-refresh/`

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-protocol-lab` (capture/replay fragility +
  drift detection).
- This is protocol-research + capture work; plan it as a lab card with concrete
  refresh/drift artifacts, not a quick fix.

## Log
- 2026-07-08 filed from the .205 runtime acceptance; positive read blocked by a
  `manager frame 3` ACK/GUID handshake mismatch on Бухгалтерия 3.0 over the LAN.
  Fail-loud correctness already proven and shipped.
- 2026-07-08T07:23:40Z `$opsx-ff` created apply-ready artifacts for
  `read-list-grid-positive-read-capture-refresh`; `openspec validate
  read-list-grid-positive-read-capture-refresh --strict` and `git diff --check
  -- openspec/changes/read-list-grid-positive-read-capture-refresh
  openspec/board` passed. Runtime [redacted third-party configuration] positive read remains an explicit
  provider gap for this Linux-only session. Next: `$opsx-do
  openspec/board/2.todo/read-list-grid-positive-read-capture-refresh.md`.
- 2026-07-08 `$opsx-do` implemented the offline capture metadata, refresh
  procedure/tooling, and manager-handshake drift detector scope; the real
  [redacted third-party configuration] positive read was not performed.
- 2026-07-08 `$opsx-do` retained the provider-gap artifact at
  `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md`,
  synced `qa-mcp-protocol-lab`, archived the OpenSpec change, and stopped before
  review/publish per supervised-run instructions.
- 2026-07-08 awaiting external review:
  `$opsx-review openspec/board/4.done/read-list-grid-positive-read-capture-refresh.md`.
- 2026-07-08T07:53:00Z external `$opsx-review` verdict validated fresh:
  `result=go`, `review_cycle=1`, findings `blocker=0`, `major=0`,
  `minor=1` (the intentionally recorded [redacted third-party configuration] positive-read provider
  gap). Publish docs review found no additional durable docs needed beyond
  `docs/capture-refresh-runbook.md`.
- 2026-07-08T07:55:35Z `$opsx-pub` final verification passed, staged only the
  manifest-owned card scope, and prepared the scoped publish commit for push to
  `origin/main`.
