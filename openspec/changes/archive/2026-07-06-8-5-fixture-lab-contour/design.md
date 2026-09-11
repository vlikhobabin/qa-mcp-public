## Context

The 8.5 lab contour is the substrate for the P2 re-capture. The single biggest
risk for the whole 8.5 epic was whether 8.5 can even stand up on this server
(conversion of an existing 8.3 file IB + a valid license under Xvfb). This change
de-risks that with a live gate before any capture work.

## Decisions

- **Convert a copy, not a fresh IB.** The `lTestClient` fixture already lives
  inside the 8.3 `vanessa_client` config; converting a copy carries it across for
  free and matches the card's guidance ("keep the original untouched"). A fresh
  8.5 IB would require rebuilding/loading the fixture.
- **Boot against the copy on an explicit Xvfb display, no Apache stop.** The 8.3
  contour's file-IB version contention (the Apache OData web module holds the
  *original* on 8.3.27.1936) does not apply to a *separate* copy file, so the 8.5
  client can boot while 8.3 OData stays up. This keeps the two contours
  independent.
- **Scope boundary.** This change proves the contour + boot + managed-desktop
  render + the runbook. Opening the fixture *form* and capturing one action is the
  adjacent change `8-5-genuine-action-capture`, because rendering that specific
  form requires the capture driver (Vanessa-on-8.5 or native), which is itself the
  capture-path decision.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason / residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient runtime | 8.5 TestClient boots + renders the converted fixture IB | live boot under Xvfb, screenshot | listening on TPort + rendered managed UI screenshot | `docs/protocol-research/evidence/card114-8-5-lab-gate-2026-06-25/85-testclient-desktop.png` | done | qa-mcp | gate proven 2026-06-25 |
| Infobase conversion | one-time 8.3→8.5 conversion of the copy | headless `DESIGNER /UpdateDBCfg` | exit 0 + config-reorg artifacts on the copy only | `/opt/1c-dev/vanessa_client_85/` (gitignored runtime) | done | qa-mcp | original 8.3 IB untouched |
| Docs/runbook | 8.5 lab-boot procedure | runbook section | committed doc section | `docs/capture-refresh-runbook.md` | planned | qa-mcp | written in `$opsx-do` |
| Fixture-form render | opening `lTestClient` on 8.5 | deferred to capture change | n/a | n/a | n/a | qa-mcp | needs the capture driver → `8-5-genuine-action-capture` |

No `src/` code changes; no role/posting/migration surfaces. The offline suite
and the 8.3 runtime path are unaffected.
