## Context

The Go host-agent started as a display bridge but now also supervises or invokes
AI for 1C COM, BSL, agent CLI, Team registration/onboarding and platform command
features. Public standalone needs only fixed-target TestClient lifecycle/relay
and bounded desktop primitives. AI for 1C is moving Windows execution to RPW,
so sharing the large agent is no longer the desired product boundary.

The bridge does not alter TestClient protocol frames. The exact Windows release
executable must prove interactive launch, TPort relay, target-window selection,
desktop-state reporting and cleanup on the authorized contour.

## Goals / Non-Goals

**Goals:**
- Publish all source for a narrow self-contained Windows bridge.
- Version its capability/API contract and fail closed on incompatible clients.
- Preserve token, lifecycle ownership, target binding and desktop safety.
- Remove every runtime dependency on other AI for 1C workstation tools.

**Non-Goals:**
- Implement Runtime Proxy/Relay or Team registration.
- Expose arbitrary process execution, filesystem browsing, COM or BSL.
- Remove authentication or allow unconstrained desktop input.
- Support a Windows copy of the Python MCP server.

## Decisions

1. Keep one Go module in the public repository but reduce the compiled command
   to reviewed standalone packages/routes. Private functions move to owning
   repositories; build tags are not used to hide a second product in public.
2. Publish an explicit major API/capability version. Python checks the handshake
   before lifecycle/display actions and rejects incompatible majors.
3. Retain health/version, launch/status/stop, authenticated TPort relay,
   window-list/target resolution, type/send-keys/click, screenshot and required
   visible-cell UIA. Remove COM, BSL, agent completion, Team onboarding/
   registration and arbitrary platform execution.
4. Preserve token-file ACL, constant-time authentication and origin checks;
   apply one post-authentication concurrency limit to every lifecycle and
   display/UIA handler, releasing capacity on success and failure.
5. Require every display/read primitive to revalidate the complete bridge-owned
   lifecycle ID/PID/TPort. Explicit window selectors remain compatibility hints
   only and cannot suppress or override that target.
6. Configure the container path through the token-authenticated fixed-loopback
   TestClient relay and qualify it with a real bounded protocol read. Default
   uninstall derives the relay firewall port from persisted owned state before
   deleting that state.
7. Cross-build the windowless Windows/amd64 executable from source-bound commit
   metadata; final acceptance runs the exact release bytes, not a local rebuild.

## Risks / Trade-offs

- [Risk] A removed route is still required indirectly by standalone doctor. →
  Define the standalone capability matrix first and make unsupported checks
  absent rather than degraded.
- [Risk] Code deletion breaks shared lifecycle helpers. → Separate packages by
  dependency direction before removing commands and retain focused Go tests.
- [Risk] Desktop E2E can act on the wrong process. → Require lifecycle ID,
  TPort/PID/window binding and fail closed before input.
- [Risk] Old clients call removed endpoints. → Major capability negotiation and
  explicit migration notes; no silent fallback.

## Migration Plan

1. Freeze the public v1 capability schema and Python client fixture.
2. Isolate retained route implementations and their dependencies.
3. Remove private routes/config/install arguments and update doctor behavior.
4. Build installer and source-bound executable; run Go and Windows E2E.
5. Publish only after lifecycle/recovery proof and exact temporary cleanup.

Rollback reinstalls the preceding signed/checksummed bridge release. The Python
client rejects incompatible versions rather than retrying unsafe primitives.

## Open Questions

- Code signing certificate availability affects trust UX but not source or
  functional release eligibility; checksums/provenance remain mandatory.

## Standalone inventory

| Class | Source/build surface |
| --- | --- |
| Retained | `main.go` authentication/capability router, TestClient lifecycle/broker/relay, target/window/desktop driver, bounded input/screenshot/UIA, token/origin/concurrency helpers, public builder and installer. |
| Removed from build and install | agent CLI, COM worker/doctor, BSL proxy/supervisor, Team registration/onboarding/bootstrap, path probe and generic platform executor handlers, flags, schemas, dependencies and tests. |
| Lifecycle-only | Platform catalog parsing and `1cv8`/`1cv8c` resolution remain internal to fixed TestClient launch; no generic execution route or arbitrary executable selector remains. |
| Public installer inputs | listener/firewall scope, token file, origins, exact executable/install/task identity, TestClient relay/TPort and lifecycle platform catalog only. |

## Verification matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason / residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient runtime | Exact Windows bridge lifecycle, relay, window/input/screenshot/UIA and cleanup against `vanessa_client` | Exact executable/hash, target, ports and current-run ownership plan | `qa_testclient_scenario`, `live_read_proof`, `screenshot` hash, `cleanup_evidence` | `.runtime/changerail/evidence/oss-05-extract-independent-open-windows-host-bridge/` | provided | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Delivery/runtime apply | Public source build, installer task/firewall lifecycle and standalone container authenticated relay read | Reproducible cross-build, route-absence, concurrency and compatibility matrix | `source_preflight`, Windows install/uninstall inventory, exact Windows concurrency tests and container `TestClientSession.read_initial()` | same evidence index plus delivery manifest | provided | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| BSL/metadata/form/role/posting/report/migration | N/A | N/A | N/A | N/A | N/A | No 1C configuration source or business data changes; residual risk is limited to host bridge/runtime compatibility and covered above. | `/opt/ai-dev-suite-for-1c/qa-mcp` |
