# team: host-agent bridge-registration rejected by the real registry (pre-audit) while a byte-identical manual POST succeeds

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Change Set
- `diagnosable-host-agent-registration-failures`

## Source
- Root T4 gate `openspec/board/1.backlog/team-t4-two-workstation-e2e-gate.md` (gap **G11**).
- Evidence: `.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260712T190912Z-full-stand/verdict.json`.
- Prior related: `team-bridge-registration-client-wire-alignment.md` (be8e32b — Bearer + `bridge_token`).

## Problem
On the 2026-07-13 real two-plane stand (team-server `.150` + Windows station `.205`,
principal `developer-a`), the host-agent (`qa-mcp-host-agent.exe`, `AgentVersion
0.1.6-bsl-supervision`, **rebuilt from HEAD so be8e32b IS included**) keeps failing bridge
registration:

- `GET /health` → `registration: {state:"error", last_error:"registry-rejected",
  attempt_count>0, configured:true}`.
- The team-registry **never records the bridge**; `/v1/bridges/developer-a` → `not_found`.
- **Crucially: the registry audit (`/var/lib/ai-suite-team/audit.jsonl`) has NO
  `bridge_registration` entry for the host-agent's attempts** → the POST is rejected at a
  **pre-audit layer** (auth/parse), not by the discovery-schema validator (which audits
  `schema_invalid`).

Yet a **byte-identical manual `curl`** POST registers fine:

```
POST http://<team-server>:28090/v1/bridges/register
Authorization: Bearer <fresh developer-a registry token>
{ "schema":"ai1c.bridge-registration.v1","user":"developer-a",
  "endpoint":"http://192.0.2.205:8001","bridge_token":"<host-agent shared token>",
  "ttl_seconds":90,
  "discovery":{ "schema":"ai1c.windows-host-bridge.discovery.v1","status":"ready",
    "platform_catalog_windows":"C:\\Program Files\\1cv8","versions":[],
    "capabilities":{...7 bools...},"diagnostics":[] } }
=> 201 {"status":"registered"}  (audit: bridge_registration status:ok)
```

## Ruled out on the stand (so it is NOT these)
- **Stale binary** — `.205` binary rebuilt from HEAD (11336704 bytes, deployed + running, be8e32b in tree).
- **Token** — `.205:reg-token-a.txt` == the freshly issued registry token (local==remote, len 43); the same token authenticates the manual POST.
- **Reachability** — `.205 → .150:28090` and `.150 → .205:8001` both open (after root G8 bind-address fix + station firewall rule).
- **Discovery schema strictness** — relaxed `windows-host-bridge-discovery.schema.json`
  (`additionalProperties:true`, lenient `versions`/`capabilities`/`platform_catalog_windows`)
  in the running registry: **still rejected** → not the discovery schema.

## ROOT CAUSE (2026-07-13, resolved by code-reading + live reproduction)
**The rejected element was the request PATH — not a header, body, or encoding.**

`registration.go` `register()` POSTs to `c.config.URL` **verbatim** (`http.NewRequestWithContext(ctx,
POST, c.config.URL, body)`) — it does **not** append the registry's endpoint path. Per the
**documented operator contract**, `-registry-url` / `QA_MCP_HOST_AGENT_REGISTRY_URL` must therefore
be the **full** URL including `/v1/bridges/register`:
- `docs/dev-mcp-suite-thin-workstation-install.md:78` → `…/v1/bridges/register`
- `deploy/workstation/examples/thin-workstation-install.example.json:32` → `…/v1/bridges/register`
- `deploy/docker/README.md:201` → "POSTs to `/v1/bridges/register` …every 30 seconds".

On the stand, `.205:ha-run-205.bat` set `-registry-url http://192.0.2.150:28090` (**base URL,
path missing**). So every registration POST hit `/` → the registry `do_POST` fall-through
`self.write_json(404, {"status":"not_found"})` — a **pre-audit 404 with no audit entry**, exactly
the observed signature. `RegistrationClient` then records the generic `registry-rejected` and moves on.

**Why the manual `curl` "byte-identical" POST worked:** it was sent to the **full path**
`…:28090/v1/bridges/register`; the host-agent was sent to `…:28090` (base). The bytes of the *body*
matched; the **request line (path) differed** — which the prior investigation (hunting header/body/
encoding) never varied. The prior "token local==remote len 43" check compared only length; content
was in fact identical and valid — the token was never the problem.

**Live reproduction against the running registry (`.150:28090`, same reg-payload.json + valid token):**
- `POST …:28090/`                     → **404 `not_found`, NO audit entry** (reproduces the host-agent failure).
- `POST …:28090/v1/bridges/register`  → **201 `registered`, audit `bridge_registration ok`**.

**Why the Go tests missed it:** `registration_test.go` fixtures use a bare `httptest` `http.HandlerFunc`
that answers **every** path (incl. `/`), so `server.URL` (base, no path) always "works" in-test. The
tests never assert the client hits `/v1/bridges/register`, so a base-vs-full URL mismatch is invisible.

## Fix applied on the stand (T4 unblock, 2026-07-13)
`.205:ha-run-205.bat` `-registry-url` → `http://192.0.2.150:28090/v1/bridges/register`; host-agent
restarted. **PROVEN:** `/v1/bridges` lists `developer-a` live @ `http://192.0.2.205:8001`;
`/v1/bridges/resolve?user=developer-a` → live w/ full discovery; audit shows the host-agent's own
`bridge_registration ok` every 30s across **6 consecutive heartbeats** (04:19:18…04:21:48), bridge
never expired. (The local resume copy `.runtime/t4-stand/ha-run-205.bat` was updated to match.)

## Goal (qa-mcp code, rescoped to diagnosability)
A host-agent registration failure must be **diagnosable from the host-agent itself** — no full
two-plane stand + raw-POST capture required. Before this delivery `register()` bounded and read the
response body but discarded its diagnostic content, logged nothing, and recorded only
`last_error:"registry-rejected"`; a simple wrong-path config (HTTP 404) was therefore invisible in
the field.

## Change 1: `diagnosable-host-agent-registration-failures`

### Why

The registry's actionable HTTP rejection is currently collapsed into a generic
health code, so a simple endpoint-path configuration error cannot be diagnosed
from the host-agent.

### Goal

Make registration failures actionable and secret-safe while preserving the
documented verbatim full-URL contract.

### Scope

- In `registration.go` `register()`, on a non-2xx response, **log** the HTTP status and a bounded
  (≤512B) snippet of the response body, and surface the status code in `last_error`
  (e.g. `registry-rejected-404`) and in the `Status()` map. Never log the tokens.
- Add a **startup sanity check / warning**: if `-registry-url` has an empty or `/`-only path
  (no `/v1/bridges/register`-style endpoint), emit a one-line warning at start — the misconfig is
  otherwise silent. (Do **not** auto-append the path: that would diverge from the documented
  full-path contract and the thin-workstation example/schema; keep the contract, add the warning.)
- Add a **client↔registry contract test** that drives the real client output through the actual
  registry `do_POST` router (so a base-vs-full URL, or any path/body mismatch, fails the test): assert
  the client requests `…/v1/bridges/register` and that the real router returns 201 + `bridge_registration ok`.

### Acceptance

- AC1.3–AC1.5 below pass with focused Go tests, the real-router loopback
  contract, and Windows-native focused verification.
- The configured registration URL is not rewritten or auto-completed.
- Logs, health and retained evidence contain no registry or bridge token.

### Depends On

- Root `deploy/docker/bin/team_registry.py` and its bridge registration schemas
  are available read-only for the suite-workspace contract test.

### Related

- `openspec/changes/archive/2026-08-01-diagnosable-host-agent-registration-failures/`

Критерии приёмки:
- [x] AC1.1 Exact rejected element identified (request **path**: base URL vs `/v1/bridges/register`); live 404-vs-201 reproduction captured.
- [x] AC1.2 Host-agent registers against the real `team_registry.py` (audit `bridge_registration status:ok`); `/v1/bridges/resolve?user=developer-a` resolves; survived **6** heartbeats. *(via stand config fix)*
- [x] AC1.3 `registration.go` logs HTTP status + bounded body on non-2xx and records the status in `last_error`/`Status()`.
- [x] AC1.4 Startup warning when `-registry-url` carries no endpoint path.
- [x] AC1.5 Regression/contract test drives the real client output through the real registry router (asserts path `/v1/bridges/register`), not a path-agnostic fixture.

## Reviewer checks
- The RCA proof uses the **real** host-agent client behavior (verbatim-URL POST) reproduced against the **real** root `team_registry.py`.
- The fix does **not** silently auto-append the endpoint path (that would break the documented full-path operator contract); it hardens diagnosis + adds a startup warning + a path-asserting contract test.

## Verify

- Focused and full Go tests, race detector, vet, and Windows cross-build.
- Focused pytest contract against the real root registry router; passing rather
  than skipped in the suite workspace.
- Windows-native focused test execution on the authorized `.205` host after
  confirming `HISTORICAL-LAB-HOST`; exact owned temporary cleanup.
- Full offline pytest, strict OpenSpec validation, and whitespace validation.
- The suite-root public-surface scanner was attempted and recorded as not
  applicable because its contract requires root-owned paths absent from this
  independent component; qa-mcp has no component scanner.

## Related
- Root T4 gate (G11) + verdict.json; `team-bridge-registration-client-wire-alignment.md` (be8e32b).
- `deploy/docker/bin/team_registry.py` `register_bridge`; `deploy/docker/schemas/bridge-registration.schema.json` + `windows-host-bridge-discovery.schema.json`.
- `openspec/changes/archive/2026-08-01-diagnosable-host-agent-registration-failures/`.

## Result
**Root cause = request-path config mismatch** (base `-registry-url` vs required full
`/v1/bridges/register`), amplified by the client swallowing the 404 diagnostic. Stand **unblocked**
by the `.205` config fix; host-agent registration was previously proven live across 6 heartbeats.
AC1.3–AC1.5 are now implemented: rejection health/logs carry a concrete HTTP status and bounded
secret-safe body, endpoint-less explicit URLs warn at startup, and the Go client passes through the
real root registry router with `bridge_registration status:ok`. The wire URL remains verbatim.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-07-13 card created from the root T4 stand G11 finding with a reproducible manual-vs-client contrast.
- 2026-07-13 **RCA found** by reading `registration.go` (verbatim-URL POST) + the documented full-path
  contract, then reproducing 404-vs-201 live against `team_registry.py`. Fixed `.205` config
  (`-registry-url …/v1/bridges/register`), restarted host-agent, proved registration + 6 heartbeats.
  Card rescoped from "capture raw POST + fix wire mismatch" to "diagnosable registration failures".
- 2026-08-01 alpha-release triage: still current as field diagnostics hardening;
  moved to `2.todo`.
- 2026-08-01 `$changerail-deliver`: created apply-ready OpenSpec artifacts for
  `diagnosable-host-agent-registration-failures`; scoped verification to
  offline real-router, Go, and owned Windows-native evidence without live 1C.
- 2026-08-01 delivery completed and archived at
  `openspec/changes/archive/2026-08-01-diagnosable-host-agent-registration-failures/`.
  RED focused Go/real-router checks failed on the missing diagnostics before
  implementation. GREEN: focused Go tests, `go test ./...`, `go test -race
  ./...`, `go vet ./...`, formatting, Windows cross-build, real-router pytest
  (1 passed), Windows-native focused tests on `HISTORICAL-LAB-HOST` (3 passed,
  owned temp removed), and offline pytest (889 passed, 71.69% coverage).
  `openspec validate --all --strict` passed (20 items after archive) and `git
  diff --check` passed. Ignored handoff evidence is listed in
  `.runtime/changerail/delivery-manifests/team-host-agent-registration-rejected-pre-audit.json`.
- 2026-08-01T22:20:45Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
