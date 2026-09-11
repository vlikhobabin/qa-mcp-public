# Runtime closure: record the Бухгалтерия 3.0 capture and prove the [redacted third-party configuration] read_list_grid positive read

## Status
4.done

## Owner
unassigned

## Order Index
130

## OpenSpec Stage
done (2026-07-08). Positive read PROVEN on [redacted third-party configuration] — see Result. The card's
original premise (a config-specific manager-handshake requiring a re-captured
"Бухгалтерия 3.0 capture") was DISPROVEN: the handshake is bound to the platform
build, not the configuration, and the bundled 8.3 capture reads [redacted third-party configuration].
Runtime-acceptance closure for the delivered card
`read-list-grid-positive-read-capture-refresh` (archived): that card shipped the
capture metadata, config-matched selection, refresh runbook/tool and the
`manager-handshake-moved` drift detector, but its **first acceptance criterion —
the actual positive read on [redacted third-party configuration] — was recorded as a provider gap**, not
proven. This card carries that gap out of the archived manifest onto the board so
it is not lost.

## Source
- Delivered card `read-list-grid-positive-read-capture-refresh` (`56ddaba`,
  4.done) left runtime checkpoint `third-party-config-positive-read-proof` = `paused`
  in `.runtime/opsx/delivery-manifests/…` (git-ignored) with next action
  "Run the documented refresh-capture and read_list_grid positive-read smoke on
  the real Windows .205 [redacted third-party configuration] host."
- 2026-07-08 .205 E2E confirmed a **new dependency**: the positive read needs a
  *persistent* client, which the host-agent launch does not yet provide (see
  F2 `host-agent-testclient-persistence-fresh-session-context`).

## Problem
No config-matched capture exists for `8.3.27.2130 / Бухгалтерия 3.0`. Against the
live base, `read_list_grid` on `Справочник.Валюты` fails at the
`manager frame 3` ACK/GUID handshake and now (post-`56ddaba`) reports the
specific `manager-handshake-moved` drift instead of a generic error — correct,
but still no positive read. Closing criterion 1 requires actually **recording**
the config-matched capture on the live base and then reading through it.

## Scope
1. Obtain a persistent client on [redacted third-party configuration]: prefer the F2 fix
   (`host-agent-testclient-persistence-fresh-session-context`); until then use an
   interactive-launched client as the runtime harness (the card family confirms
   interactive launches persist).
2. Run the refresh-capture procedure from `docs/capture-refresh-runbook.md` on
   the live `8.3.27.2130 / Бухгалтерия 3.0` base to record the irreducible
   session-bootstrap + list-open/read templates; write the sanitized capture
   metadata sidecar (raw pcaps/traffic stay in ignored runtime paths).
3. Select the config-matched capture at read time and prove the positive read.
4. Replace the provider-gap artifact
   (`…/third-party-config-positive-read-provider-gap.md`) with a **sanitized** MCP/QA
   proof bundle (no credentials, screenshots or customer data).

## Acceptance
- `read_list_grid` on `Справочник.Валюты` ([redacted third-party configuration], 8.3.27.2130,
  Бухгалтерия 3.0) returns the visible row(s) using the config-matched capture.
- A sanitized proof bundle replaces the provider-gap artifact.
- Regression: demo10413 and other proven configs still read correctly.

## Result

**PROVEN 2026-07-08 (supervised live session, historical-user .201).** `read_list_grid`
on `e1cib/list/Справочник.Валюты` returned visible rows on **[redacted third-party configuration]**
(8.3.27.2130), reproduced 3× first-try:

```
{"table":"Валюты","row_count":10,
 "rows":[{USD,840},{EUR,978},{TRL,792},{у.е.,001},{руб.,643},{KZT,398},{BTC,BTC}...],
 "list_refresh":{"method":"f5","poll_outcome":"nonzero"},
 "table_resolution":{"opened":"Валюты","available_tables":["Валюты"]}}
```

Regression proven the same session: **demo10413** → 10 rows (EUR/USD/Рубли);
**vanessa_client** → 0 rows (catalog genuinely empty, list opened + read cleanly).
All via the released container (`qa-mcp-thin:v0.2.4`), driven locally on .201
with the **bundled 8.3 capture** — no config-matched re-capture, no Vanessa
TestManager.

**Root-cause correction.** The prior `manager-handshake-moved` was NOT
config-specific protocol drift. The handshake is platform-build-bound (proven:
same 8.3 capture reads [redacted third-party configuration] and demo10413). The real prerequisites for the
[redacted third-party configuration] read were purely environmental:
1. Correct 1C user `[redacted 1C user]` (no password) — a wrong user makes
   the client bind its TPort ~4s then die (`Пользователь ИБ не идентифицирован`),
   which then surfaces downstream as reset / "Network unreachable" / handshake
   errors.
2. Correct `QA_MCP_HOST_AGENT_WINDOW` = `Бухгалтерия предприятия, редакция 3.0`
   for the F5 list refresh (the container default targeted demo10413's window),
   else `row_count:0, "no display backend was reachable"`.
3. Drive locally (host-agent :8001 is firewalled from cross-LAN); the frame-3
   ACK failure is intermittent single-manager-session state — retry.

Follow-up (usability, not a Proof-B blocker): the F5-refresh window is a hardcoded
env; auto-detecting the client's own top-level window per launch would remove the
per-config `QA_MCP_HOST_AGENT_WINDOW` override.

## Change 1: `read-list-grid-third-party-config-positive-read-runtime-closure`

### Why
The delivered capture-refresh tooling is unproven end-to-end until a
config-matched capture is actually recorded on Бухгалтерия 3.0 and the positive
read is demonstrated; the closure currently lives only as a paused runtime
checkpoint in an archived manifest.

### Goal
Record the Бухгалтерия 3.0 config-matched capture on the live base and prove the
`Справочник.Валюты` positive read, retaining a sanitized proof bundle.

### Acceptance
- As in the card Acceptance.

### Depends On
- `host-agent-testclient-persistence-fresh-session-context` (F2) for a persistent
  client — OR an interactive-launched client as the runtime harness.

### Related
- `read-list-grid-positive-read-capture-refresh` (archived; tooling),
  `docs/capture-refresh-runbook.md`, epic 111 item 4.

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-protocol-lab`.
- This is live protocol-recording work; the positive-read proof is runtime
  evidence on the real host (record a provider gap only if the host is
  unavailable). Keep raw capture payloads out of git.

## Log
- 2026-07-08 filed to carry the delivered card's paused runtime checkpoint
  (`third-party-config-positive-read-proof`) onto the board; the .205 E2E added the F2
  persistent-client dependency.
- 2026-07-08 (supervised live .205) partial progress:
  - **Persistent-client prerequisite MET** via the documented interactive-client
    fallback (Scope 1): an interactive scheduled-task `1cv8 /TESTCLIENT`
    persisted > 60 s (325 s observed), TPort 15381 on `0.0.0.0`, LAN-reachable.
    The F2 dependency is **removed as a blocker** — F2's host-agent launch is
    disproven on this host (see
    `host-agent-testclient-persistence-interactive-launch-mechanism`), so this
    card should rely on the interactive-launch harness.
  - **Positive read still blocked (unchanged).** With the persistent client,
    `read_list_grid` on `Справочник.Валюты` returns `manager-handshake-moved`
    (frame 3, `client ACK GUID not found`, `response_byte_count: 0`) — the
    config-specific manager-handshake drift for Бухгалтерия 3.0, exactly as
    card2's drift detector reports. Reproduced live.
  - **Remaining blocker narrowed to Scope 2** only: record a config-matched
    Бухгалтерия-3.0 capture (genuine Vanessa TestManager → `protocol_proxy` →
    the .205 client, per `docs/capture-refresh-runbook.md` §3). Operator elected
    to DEFER this to a dedicated capture session; it touches the retired Vanessa
    TestManager tooling + license and is a focused multi-step effort.
- 2026-07-08 (later, historical-user .201) — **the Scope-2 "config-matched capture" premise
  above was DISPROVEN and the card is DONE.** Operator corrected: the handshake is
  platform-build-bound, not config-specific; the released qa-mcp already passes on
  [redacted third-party configuration]. Re-tested on .201 → positive read of Валюты PROVEN (10 rows) with the
  BUNDLED 8.3 capture; no re-capture / Vanessa TestManager needed. See Result. The
  real prerequisites were correct 1C user + correct F5-refresh window + local drive.
