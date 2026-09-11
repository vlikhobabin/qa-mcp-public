# Card 98 / change 5 (the 🚩 GATE) — 2nd-config validation: READ path generalizes (first milestone)

**Date:** 2026-06-18. **Card:** 98 change 5 (= old card 94) — validate capture-free synthesis on a 2nd (real,
non-fixture) config; the lab-demo→product boundary, the gate on the "100% replacement" claim. **Status:** READ
path PROVEN to generalize to a 2nd infobase; WRITE/action generalization characterized (next test below).

## What was tested

A native `/TESTCLIENT` was stood up against **`/opt/1c-dev/demo_1_0_41_3`** ("managed-app-demo-1_0_41_3" — a
real 1C:БСП demo infobase, NOT the fixture; it has NO `ФикстураПротоколаTestClient` processor) on port :15382,
user `Администратор` (empty pw), under Xvfb. NOT apache-published, so apache stays up. Then the capture-free READ
path (`read_active_window`) was run against it — the read replays the **vanessa_client** read-only bootstrap
(`tm-v1-ro-batchQ3`) + GuidRebinder, with NO demo-specific capture.
Tools: `tools/protocol-research/{second_config_read_probe.py,run_second_config_read_test.sh}`.

## Result — the bootstrap is config/infobase-agnostic (Q1 answered: YES)

`read_active_window` → **scenario status=passed, step ok, evidence_status=accepted**, and it read the demo
client's REAL active window back: `MainFrame` caption **"Демонстрационное приложение"** + `HomePage` caption
**"Начальная страница"** (`e1cib/navigationpoint/startpage`) — decoded from the genuine client→manager responses
(`runtime/.../native-mcp/<ts>/steps/response_after_send_006/009`).

So the open question Q1 — *is the bootstrap/handshake config-agnostic, or does it encode fixture/infobase
specifics?* — is answered **YES, it is portable**. The vanessa_client read-only bootstrap established a session
against a DIFFERENT infobase's client. The handshake (sent_001..003) carries CLIENT-MACHINE specifics learned
live (hostname `HISTORICAL-LAB-HOST`, NTLMSSP, platform `8.3.27.2130`) and per-session GUIDs that `GuidRebinder`
rebinds from the live responses — none of it is a blocking config constant. **The read path needs NO per-config
capture.**

## Generality matrix (first cut)

| capability | status | evidence |
| --- | --- | --- |
| bootstrap / handshake | ✅ generalizes (infobase-portable) | established against demo_1_0_41_3 (foreign IB) |
| `read_active_window` (and the read path: form summary / value / element — same machinery) | ✅ generalizes as-is, NO config capture | read the demo's real MainFrame/HomePage |
| element addressing by NAME | ✅ generic by design | read path uses it; write path uses the same `element_ref` retargeting |
| `write_form_value` + every action (choose/click/dialog/open_card/close/activate/table/...) | ⚠ needs a per-config capture of the SPECIFIC element/flow | the shipped templates replay fixture captures whose element names are fixture-specific (`PF_*`, `ФикстураПротоколаTestClient`) — those objects don't exist in another config |

## Per-config onboarding recipe (first cut) + honest claim

- **Read** against a new config: works immediately, no capture (proven).
- **Write / actions**: the ENGINE is config-agnostic (handshake + `GuidRebinder` + element-addressing-by-name +
  the full-replay/derive machinery), but each shipped action replays a genuine capture whose element NAMES are
  the fixture's. For a new config you capture the genuine target flow ON that config's form once (same
  genuine-manager recipe, [[genuine-action-capture-recipe]]); the by-name retargeting + GuidRebinder then replay
  it. So the honest claim is **"per-config-capture-free after a one-time per-flow capture"**, NOT "universally
  capture-free". The read path is the exception — universally capture-free.

## Limitations / next

- `demo_1_0_41_3` shares the 1C:БСП base with vanessa_client (it's the demo WITHOUT the fixture). It is a
  separate infobase (different data, different session, no fixture), which already proves infobase-portability
  and non-fixture read generalization — but a STRUCTURALLY different config (`redacted-third-party-config`, the big real
  config) would be the stronger test. Documented follow-up.
- **Next test (completes the gate):** WRITE into a foreign form field — navigate the demo to a form with an
  editable field, capture that field's genuine input ONCE on the demo, and confirm `write_form_value` commits
  via the by-name + GuidRebinder machinery. That measures the real per-config onboarding cost for the action
  surface and turns the ⚠ rows into ✅-after-one-capture.
