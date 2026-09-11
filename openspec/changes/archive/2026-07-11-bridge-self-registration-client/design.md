## Context

The Windows host-agent currently serves authenticated bridge operations but has no team registry client. Root owns the pending registry service and schema; qa-mcp owns the client. Decision-freeze #1--#8 and R24--R27 are inputs: this change neither revisits static versus dynamic registration nor changes git, per-user index, source-transport, or embedding policy.

## Goals / Non-Goals

**Goals:**
- opt-in startup registration plus periodic heartbeat;
- immutable configured user and secret-safe failures;
- bridge availability independent of registry availability;
- deterministic Linux fixture coverage and retained provider gaps for the supervised stand.

**Non-Goals:**
- registry storage/resolution, gateway identity, provisioning, or per-seat logic;
- live Windows/team-server proof in this run;
- TestClient protocol changes or live 1C operations.

## Decisions

1. **A dedicated lifecycle client owns registration.** `main` constructs it from immutable startup configuration and starts it beside the HTTP server. No request can replace the registered user in memory.
2. **Configuration is fail-closed when partially enabled.** Registry URL, user, token, and advertised endpoint are required together. With no registry URL, the client is disabled and performs zero network calls. Invalid partial configuration prevents host-agent startup rather than sending ambiguous identity.
3. **The heartbeat is fail-soft for bridge service.** Registration failures update bounded status and retry only at the next heartbeat; they never stop the host-agent HTTP server.
4. **The request is a bounded JSON envelope.** It carries schema, user, endpoint, token, TTL seconds, and a discovery body derived locally. The token is never included in status, logs, test evidence, or error text.
5. **The fixture validates the wire contract independently.** The registry
   fixture decodes raw JSON into generic values and validates it with a frozen
   `ai1c.bridge-registration.v1` JSON Schema; it never unmarshals into the
   producer's `registrationEnvelope`. A dedicated negative case proves that
   renaming `ttl_seconds` to `ttl` is rejected.
6. **Offline proof is authoritative for this delivery.** An `httptest` fixture controls accepted/rejected responses, request count, registry reset, and lease expiry. Recovery is bounded by one configured heartbeat plus 100 ms scheduler tolerance, kept below two heartbeats. A real Windows agent and the root registry service are explicitly not claimed.

## Risks / Trade-offs

- Root schema is delivered by a parallel card -> keep the envelope isolated and cover its exact emitted shape; live schema round-trip remains a provider gap.
- Registry downtime can leave no live route -> retry at the next heartbeat and surface last success/error without degrading local bridge functions.
- A wildcard listener is not a reachable endpoint -> require an explicit advertised endpoint whenever registration is enabled.

## Migration Plan

Existing installs omit registry configuration and remain in solo mode. Team installs add the four required registry values and may override heartbeat/TTL. Removing the registry URL rolls back to solo behavior.

## Open Questions

None for qa-mcp. Root schema/service compatibility is a supervised integration checkpoint, not a reopened design fork.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | host-agent registration lifecycle and team registry request | independent schema fixture covering wire drift, startup, heartbeat bound, reset, rejection, expiry, bridge-operation availability and solo mode | source_preflight, scenario_log, data_assertion | `.artifacts/openspec/bridge-self-registration-client/2026-07-11-cycle2/offline-verification.txt` | required |  |  | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Delivery or runtime apply | real Windows host-agent to root registry | supervised Windows launch plus live `ai1c.bridge-registration.v1` round-trip | runtime_apply_log, scenario_log | `.artifacts/openspec/bridge-self-registration-client/2026-07-11/windows-stand/` | blocked |  | Live endpoint reachability and server schema compatibility remain unproved offline | `/opt/ai-dev-suite-for-1c/qa-mcp` |

### Provider Gaps

| provider_id | owner_path | matrix_row | missing_capability | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | real Windows host-agent to root registry | supervised Windows host-agent and live root registry service are outside this offline run | runtime_apply_log, scenario_log | live endpoint reachability and server schema compatibility remain `unverifiable` | verify client behavior against the independent in-process schema fixture; run the live pair on the supervised stand | `openspec/board/3.inprogress/team-host-agent-self-registration-and-bsl-supervision.md` | `.artifacts/openspec/bridge-self-registration-client/2026-07-11/provider-gap-windows-live-registry.md` |
