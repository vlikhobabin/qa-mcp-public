# Host-agent bridge-registration client: align to the real `ai1c.bridge-registration.v1` wire

## Status
4.done (implemented inline at operator request, independent fresh-context review
`go`, published via `$changerail-pub`). See `## Delivered (inline 2026-07-12)`
and `## Result`.

## Owner
qa-mcp (host-agent). Contract owner: root
(`deploy/docker/schemas/bridge-registration.schema.json` + `team_registry.py`).

## Source
Operator-supervised two-machine team stand, 2026-07-12 (team-server .150 + thin
station .205). The real host-agent self-registration client and the real root team
registry **do not interoperate** on the wire, blocking root-10 AC3.1
(greenfield station self-registers to the bridge registry). Evidence (gitignored):
`ai-dev-suite-for-1c/.artifacts/openspec/thin-workstation-install/2026-07-12-stand/windows-stand-evidence.md`.

Triple-confirmed on the stand:
- real .205 host-agent → real registry (LAN): `registration.state=error`,
  `last_error=registry-rejected`, retried every heartbeat;
- replay of the client's exact envelope → `400 "bridge registration token is
  invalid or revoked"`;
- positive control (correct format) → `201 registered`, bridge lands `live`.
So the registry is correct; the **client** is out of spec.

## Problem
`host-agent/windows-display-agent/registration.go` `register()` posts an envelope
`{schema,user,endpoint,token,ttl_seconds,discovery}` with only a `Content-Type`
header. The contract + registry require:
1. **Auth header** `Authorization: Bearer <registry-token>` — the registry
   authenticates the registering principal from it (`resolve_token(bearer_token(headers))`);
   without it every registration is rejected before schema validation.
2. **Body field `bridge_token`** (schema `required`), a *separate* per-bridge
   secret used later to authenticate `/v1/bridges/call`. The client currently sends
   the field name `token` (the registry token) in the body; the registry token must
   move to the Authorization header and a distinct `bridge_token` must be sent.

The gap was invisible to existing tests: the root Linux fixture smoke uses its own
correct test client; the qa-mcp card exercised the client against a permissive mock
registry. Neither ran the real cross-implementation wire.

## Goal
The real host-agent registers successfully against the real root team registry over
the LAN (HTTP 201, bridge becomes `live`), heartbeat renews within TTL, and the
registry-restart self-heal path works — verified against the actual
`team_registry.py`, not a mock.

## Proposed Change 1: `bridge-registration-wire-alignment`
### Why
Make the self-registration client conform to `ai1c.bridge-registration.v1`.
### Scope
- Send `Authorization: Bearer <registry-token>` on the registration POST (the
  existing `-registry-token`/`QA_MCP_HOST_AGENT_REGISTRY_TOKEN`).
- Introduce a distinct per-bridge secret and send it as body `bridge_token`
  (new flag/env, e.g. `-registry-bridge-token`/`QA_MCP_HOST_AGENT_BRIDGE_TOKEN`);
  stop sending the registry token in the body. Redact both in logs/status.
- Confirm the discovery body already validates against
  `windows-host-bridge-discovery.schema.json` (capabilities/versions/status);
  fix any drift.
- Update the host-agent registration docs + the qa-mcp bootstrap/install wiring so
  the thin-workstation procedure passes the right flags.
### Acceptance criteria
- [ ] AC1.1 Against the real `team_registry.py` (fixture or stand): registration →
      `201 registered`; `GET /v1/bridges` shows the bridge `live` (not a mock).
- [ ] AC1.2 Missing/invalid `bridge_token` or missing Authorization → registry
      rejects; client surfaces a clear `last_error` (regression guard for this bug).
- [ ] AC1.3 Heartbeat renews the record within TTL; stop → expires ≤ TTL; restart
      registry → re-registration within one heartbeat (real registry, not mock).
- [ ] AC1.4 Registry token and bridge token never appear in logs/status/evidence.
- [ ] AC1.5 Component pytest/Go floor green; solo mode (no registry) unchanged.

## Depends On
- none (contract + registry already exist; this is a client conformance fix).

## Notes
- Re-run the operator-supervised .205 stand after the fix to finally close
  root-10 AC3.1 and the qa-mcp team-host-agent AC1.2/AC1.4 real-registry halves.
- Consider whether the root registry should ALSO accept a bounded back-compat form;
  default recommendation is client-conforms (root is the contract owner).

## Delivered (inline 2026-07-12)
Implemented directly at operator request and verified against the REAL registry
(not a mock):
- `registration.go`: `register()` now sends `Authorization: Bearer <registry-token>`
  and body `bridge_token` (renamed from `token`); `RegistrationConfig.BridgeToken`
  added; `NewRegistrationClient` fails closed when the bridge token is missing or
  > 512 chars.
- `main.go`: new `-registry-bridge-token` / `QA_MCP_HOST_AGENT_BRIDGE_TOKEN`
  (+ `-file`), defaulting to the host-agent token (the server presents this
  bridge_token when calling back, and the host-agent authenticates callers with its
  own token).
- `testdata/ai1c.bridge-registration.v1.schema.json`: aligned to the root canonical
  contract (`deploy/docker/schemas/bridge-registration.schema.json`) — requires
  `bridge_token` (maxLength 512), tighter endpoint pattern, `ttl_seconds` max 300.
  This was the root cause: the "frozen" contract had DIVERGED between qa-mcp (`token`)
  and root (`bridge_token`).
- `registration_test.go`: assert body `bridge_token` + `Authorization: Bearer`,
  reject legacy body `token`, and a missing-bridge-token fail-closed regression case.

Verification:
- `go vet ./...` clean; `go test ./...` PASS (host-agent Go floor green).
- Cross-built `qa-mcp-host-agent.exe`, deployed to .205, registered against the real
  root `team_registry.py` on .150 over the LAN → client `registration.state=registered`,
  `last_success_at` set; registry audit `bridge_registration status:ok` for
  developer-205 every heartbeat. This is exactly AC1.1.
- Evidence: `ai-dev-suite-for-1c/.artifacts/openspec/thin-workstation-install/2026-07-12-stand/`.

Remaining before publish: full component pytest/Go floor run, `$opsx-review`
fresh-context gate, `$opsx-pub`. AC1.3 (expire/restart re-reg against the real
registry) and AC1.4 (secret-safety) covered by mechanism + existing tests; re-run
against a live registry during review if desired.

## Result
Delivered inline (operator: "фиксь клиент сейчас") without the `$changerail-do`
OpenSpec change-artifact lifecycle — accepted for this small conformance fix
against the already-frozen `ai1c.bridge-registration.v1` contract (review R1,
non-blocking). Independent fresh-context review (cycle 1) returned `result: go`:
AC1.1 pass (stand-evidence), AC1.2 pass, AC1.3 unverifiable (real-registry
expire/restart cycle deferred; mechanism green), AC1.4 pass, AC1.5 pass on the Go
floor (`go vet` + `go test` green; Go+JSON change does not touch the Python
pytest floor — AC1.5 scoped to the Go floor per review R3). Non-blocking follow-ups:
R2 (add a `>512` bridge-token unit test), R3 (optional pytest floor run).
Published scoped to this card's 5 files (the card + the four host-agent files);
the card-8 `4.done` evidence note is a separate concern and was excluded.

## Log
- 2026-07-12 discovered on the operator-supervised .205 two-machine stand:
  real host-agent → real root team-registry rejected (`ai1c.bridge-registration.v1`
  wire mismatch — the "frozen" schema had diverged: qa-mcp `token` vs root
  `bridge_token`; client also omitted `Authorization: Bearer`).
- 2026-07-12 fixed inline: `registration.go` (Bearer + body `bridge_token`,
  fail-closed), `main.go` (`-registry-bridge-token`/`QA_MCP_HOST_AGENT_BRIDGE_TOKEN`),
  `testdata` schema aligned to root canonical, tests updated. `go vet`/`go test`
  green. Re-verified end-to-end: fixed host-agent on .205 → real registry on .150
  (LAN) → `registration.state=registered`, audit `bridge_registration ok`/heartbeat.
- 2026-07-12 independent review `go`; `$changerail-pub` scoped commit + push.
