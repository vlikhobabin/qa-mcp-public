# 121. qa-mcp product license gate — integrate the suite ai1c-license broker (per-user, 14-day offline grace)

## Status
4.done

## Result
✅ **DONE 2026-07-07 via the v0.3.0 self-hosted release.** The only remaining
piece (Ch3 `license-activation-bootstrap`) was delivered: `bootstrap.ps1`
activates a per-deployment `ai1c-license` lease into a private volume on first
start and the startup gate ships **ON** (`QA_MCP_LICENSE_GATE=1`). Verified
end-to-end on a clean Windows 11 laptop (.205): bootstrap → license activated
against the public server (`…:58443/license`) → gate ALLOWS → MCP serves 63
tools; no-lease ⇒ provider down. See [[qa-mcp-standalone-release-proven]].
(Cross-repo `license-server-config` remains owned by root/`license/`.)

## Order Index
121

## Owner
unassigned

## OpenSpec Stage
artifacts

## Change Set
Ordered, apply-ready (validated `--strict`); capability `qa-mcp-license-gate`.
2026-07-06 board triage: Ch1 and Ch2 are delivery-complete and archived. The
only qa-mcp implementation change that remains is Ch3.

1. `openspec/changes/license-gate-startup/` — DONE. Gate in `mcp_server.main()`,
   `QA_MCP_LICENSE_GATE` OFF by default, fake-broker contract matrix.
2. `openspec/changes/license-broker-in-image/` — DONE for the image/delivery
   surface. The gate-bearing modules are compiled/non-removable by cards 122/123;
   the current host-stable anchor is `AI1C_LICENSE_FINGERPRINT` + the
   `qa-mcp-license` volume, not an `/etc/machine-id` bind.
3. `openspec/changes/license-activation-bootstrap/` — REMAINING. First-start
   activation in `bootstrap.ps1` + runbook; turn the gate ON in the shipped run.
4. `license-server-config` — **cross-repo coordination, owned by root/`license/`**
   (NOT a qa-mcp OpenSpec change): the server is deployed + running on `:8791`;
   remaining is config (public URL + open `:8791`, 14-day grace, per-user
   entitlement). Tracked here as the external dependency that flips the gate live.

## Progress (per change)
- **Ch1 `license-gate-startup`** — DONE (committed `d828f53`), gate OFF by default
  (`QA_MCP_LICENSE_GATE`); compiled non-removable by card 123-Ch2. Archived as
  `openspec/changes/archive/2026-07-06-license-gate-startup/`.
- **Ch2 `license-broker-in-image`** — **DONE 2026-06-29, committed + pushed as
  `37586e2`, with follow-up corrections `480df7c` and delivery rebuilds.** Decision D1 was
  Option A (vendored static binary) and the current protected image also accepts the suite-base
  broker path checked by `docker/verify_protected_image.py`. The important current contract is:
  broker executable present in-image; `QA_MCP_LICENSE_BROKER` points at the shipped broker;
  `AI1C_LICENSE_LEASE_PATH`/`AI1C_LICENSE_KEYSET_PATH` point at `/var/lib/qa-mcp/license`;
  host identity is supplied by `AI1C_LICENSE_FINGERPRINT`; `qa-mcp-license` volume persists
  lease/offline-grace state. Archived as
  `openspec/changes/archive/2026-07-06-license-broker-in-image/`. Remaining live
  activation/restart/grace proof belongs to Ch3.
- **Ch3 `license-activation-bootstrap`** — NOT STARTED. Decisions now resolved on the
  qa-mcp side: Windows host id = registry `MachineGuid` passed as
  `AI1C_LICENSE_FINGERPRINT`; gate-bearing modules are compiled/non-removable. Still
  pending: confirm public `:8791` reachability/entitlement policy in root `license/`,
  wire activation UX, then enable `QA_MCP_LICENSE_GATE=1` in the shipped run.

## Next
- **Resume at Ch3 only.** Ch1 + Ch2 are archived as completed board hygiene.
  Remaining = activation UX + shipped gate ON + cross-repo `license-server-config`
  (public URL/firewall/entitlements/grace) in root `license/`.
- On resume: confirm external `:8791` reachability from outside the LAN and the entitlement
  issuance policy, then `$opsx-do` Ch3.

## Source
- 2026-06-26 public-delivery prep. User decision (AskUserQuestion): give the public qa-mcp delivery a **product
  license** — per-user, working **2 weeks offline** — by **integrating the suite `ai1c-license` broker** (not a
  bespoke trial). Memory [[qa-mcp-public-delivery-prep]].
- The root coordination contract **mandates** component-local implementation:
  `docs/dev-mcp-suite-provider-startup-license-gates.md` ("Component implementation belongs to the owning provider
  repositories"). qa-mcp was explicitly **not in the first wave**; this card adds it, following the proven pattern.

## Decision (FIXED 2026-06-26)
Adopt the **provider startup license gate** already shipped by `help-/knowledge-/meta-/live-mcp`. qa-mcp gates its
own MCP startup on the native broker; the broker owns leases, fingerprint and the offline-grace window.

## The proven contract (verified against the root doc + 4 shipped providers)
Startup runs the native broker and **fails closed** unless allowed:
```
ai1c-license check --component qa-mcp --json
```
**ALLOW** only when ALL hold: exit code `0`; `allowed: true`; status `licensed` **or** `offline_grace`; response
schema + component match. On `offline_grace` → start, but surface the grace (incl. the broker grace timestamp) in
diagnostic-safe startup output. **DENY** (fail closed) on: non-zero exit, `allowed:false`, missing/unlaunchable
broker, timeout, malformed JSON, unsupported schema, component mismatch, no lease, denied entitlement,
expired lease/grace, invalid signature, unknown/revoked key, fingerprint mismatch. **Diagnostic safety:** never
log keys, raw hardware ids, customer/1C/infobase/path data, traces, screenshots, credentials (root contract §
Diagnostic Safety). The broker BUILDS for linux/amd64 (`go build ./cmd/ai1c-license`, ~9 MB) so it ships in the
thin image.

## The model-B container wrinkle (the one real design delta vs the 4 host-run providers)
The fingerprint binds a lease to "one local installation" from local signals (`machine-fingerprint-v1`). A thin
container is **ephemeral** → its fingerprint + lease state would reset every run, so a naive in-container broker
never holds a per-user lease. Current solution:
- **Host-stable fingerprint:** `bootstrap.ps1` obtains a stable Windows host id
  (registry `MachineGuid`) and passes it into the container as `AI1C_LICENSE_FINGERPRINT`
  so the broker fingerprints the **host**, not the container.
- **Persistent lease state:** mount a named volume (e.g. `qa-mcp-license:/var/lib/qa-mcp/license`) for the
  broker's activation/lease cache so the lease + offline-grace survive container recreation.
- Alternative considered (defer): run the gate from the **host agent** (already host-persistent) and have the
  container trust it — rejected for v1 (couples licensing to the optional display agent; the broker-in-container
  + mounts path is simpler and matches the existing model-A identity-mount precedent).

## Activation + the server dependency (RESOLVED 2026-06-27 — server is up)
- The broker's `check` consumes a signed lease; the lease is obtained by **online activation** (first start →
  contact the **`ai1c-license-server`**). There is **no offline self-issued trial in the broker today** (verified:
  no trial/self-issue path in the Go source). So "2 weeks offline" = the **offline-grace window AFTER a one-time
  online activation**, and "per-user, on first start" = **online activation on first start**.
- ✅ **The license server IS DEPLOYED + RUNNING (2026-06-27):** `/opt/ai1c-license-server/bin/ai1c-license-server`
  (long-running PID), listening on **`0.0.0.0:8791`**, with `secrets/` (signing keys) + `state/` (activation
  records). The earlier "must deploy a server" dependency is **satisfied** — the live activation path is feasible
  now. Remaining server-side items (root/`license/`): point the in-container broker at the **public URL** of this
  server (not localhost) + open `:8791` to the internet; configure the **14-day grace** + the **per-user
  entitlement** issuance policy.

## Enforceability — current state
A license gate in readable `.py` is trivially bypassable. This prerequisite is now satisfied for the shipped
image: cards 122/123 and follow-up delivery fixes compile `mcp_server.py` + `license_gate.py` into native modules
and `docker/verify_protected_image.py` asserts the gate-bearing sources are absent and compiled modules are
present. Therefore Ch3 may turn the gate ON once activation/server config is live. The dev source remains readable;
the enforceability claim applies to the protected delivery image.

## Proposed Change Set (for `$opsx-ff`; ordered)
1. **`license-gate-startup`** — qa-mcp side, self-contained + testable WITHOUT a server (fake-broker fixtures).
   Add a startup gate in `mcp_server.main()`: run `ai1c-license check --component qa-mcp --json` (configurable
   broker path/timeout), parse, ALLOW/DENY per the contract, surface `offline_grace` diagnostic-safely. Gate is
   **env-flagged** (`QA_MCP_LICENSE_GATE=1`) and **OFF by default** so the current free delivery is unaffected
   until the server side is ready. Tests cover allowed / offline_grace / denied / malformed / missing-broker /
   timeout (the contract's required matrix). Capability: startup license gate.
2. **`license-broker-in-image`** — ship `ai1c-license` in the thin image; add `AI1C_LICENSE_FINGERPRINT` +
   `qa-mcp-license` lease volume wiring to compose/docs; CI/protected-image verification confirms the broker is
   present. Capability: broker delivery + persistent license anchor.
3. **`license-activation-bootstrap`** — `bootstrap.ps1` + runbook gain the first-start **activation** step
   (prompt for / pass the entitlement, run the broker activate against the server) and the
   `AI1C_LICENSE_FINGERPRINT` + lease-volume wiring; turn the gate ON (`QA_MCP_LICENSE_GATE=1`) in the shipped
   run. Capability: activation UX.
4. **`license-server-config`** (coordination, root/license) — the server is already **deployed + running**
   (`/opt/ai1c-license-server`, `:8791`); remaining is **config**: expose a public URL + open `:8791`, set the
   **14-day grace**, and the **per-user entitlement** issuance policy. Implemented in the license workspace.
   Capability: license issuance (cross-repo coordination).

(Build 1 first — it lands the gate + tests with zero live dependency and zero impact on the current delivery.
Builds 2–3 wire delivery; build 4 is the external dependency that flips it live.)

## Acceptance
- qa-mcp startup gate matches the root contract: ALLOW only on exit0+`allowed`+`licensed`/`offline_grace`;
  fail-closed on every deny case; `offline_grace` surfaced diagnostic-safely; no sensitive data in diagnostics.
- Off-by-default (`QA_MCP_LICENSE_GATE` unset) → current delivery unchanged; on → enforced.
- Container holds a **per-host** lease across restarts (`AI1C_LICENSE_FINGERPRINT` + lease volume); **14-day
  offline grace** works with the server unreachable after a one-time activation.
- Test matrix green (allowed/grace/denied/malformed/missing-broker/timeout).
- The license-server dependency is documented + coordinated with the root/`license/` workspace.

## Open questions
- Confirm the broker's grace window is configurable to **14 days** (and where).
- Confirm the per-user **entitlement issuance** flow on the server (manual vs self-serve at first start).
- Decide diagnostics surface for `offline_grace` (startup log line / a status MCP tool?).

## Pointers
- Root contract: `docs/dev-mcp-suite-provider-startup-license-gates.md`; broker contracts
  `license/contracts/{cli-status-check,machine-fingerprint,signed-lease,exit-codes}-v1.md`.
- Proven precedent (copy the pattern): `meta-mcp` / `live-mcp` / `knowledge-mcp` / `help-mcp` startup gates
  (`*/openspec/board/4.done/2026-06-03T17-1*-provider-startup-license-gate.md`).
- Broker source: `license/ai1c-license/` (builds: `GOOS=linux GOARCH=amd64 go build ./cmd/ai1c-license`).
- qa-mcp entrypoint to gate: `src/qa_mcp/mcp_server.py:main()`; delivery wiring `docker/Dockerfile.thin`,
  `docker-compose.thin.yml`, `delivery/bootstrap.ps1`, `delivery/windows-agent-runbook.md`.
- Model-A host-stable identity precedent (the container-anchor pattern): `docker/run-host-platform.sh`.

## Log
- 2026-06-26 created from the public-delivery license decision. Confirmed: broker builds for linux/amd64; the
  proven 4-provider startup-gate pattern applies; the model-B delta is the ephemeral-container fingerprint
  (now solved by `AI1C_LICENSE_FINGERPRINT` + lease volume); the live gate depends on a deployed `ai1c-license-server`
  (no offline self-trial in the broker today). 4-change set recorded; change 1 (the gate + tests) is buildable
  now with zero live dependency and OFF by default.
- 2026-06-27 `$opsx-ff`: decomposed into 3 apply-ready qa-mcp OpenSpec changes under a NEW capability
  `qa-mcp-license-gate` (all valid `--strict`): `license-gate-startup`, `license-broker-in-image`,
  `license-activation-bootstrap`. Change 4 (`license-server-config`) is KEPT as a cross-repo coordination
  dependency owned by root/`license/` — NOT generated as a qa-mcp OpenSpec change (ownership boundary per
  AGENTS.md). Confirmed `main()` is a clean single startup choke point (~line 2851) for the gate. Card → 2.todo,
  stage → artifacts. Next = `$opsx-do` Change 1 (build OFF; enforce only after card 122 compiles it).
- 2026-07-06 board hygiene: Ch1/Ch2 are treated as completed delivery slices and removed from the active
  work queue; Ch3 remains the only qa-mcp implementation work. Current fingerprint mechanism is
  `AI1C_LICENSE_FINGERPRINT`, not an `/etc/machine-id` bind; gate compilation prerequisite is already satisfied.
