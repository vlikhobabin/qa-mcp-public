## Context

`testclient-launcher-libgcc-and-attach` added Linux libgcc preload handling, launch diagnostics and
`attach_test_client()`. The attach function validates a listening TPort and returns a non-owned
`TestClientProcess`-shaped handle, but the MCP tool currently returns only a status dictionary. Descriptor,
read, write and scenario tools still instantiate `TestClientSession(host, port)` directly at each call site.

The delivery review found that this leaves the original B7 blocker unsolved: a client launched out-of-band can be
reported as listening, but `read_form_descriptor(open_link=..., enumerate_live=true)` can return
`{opened:null, fields:{}}` for an existing form. The fix must either make the attached endpoint the real session
route for protocol tools or expose a precise bootstrap diagnostic if the foreign-launched client cannot be driven.

## Goals / Non-Goals

**Goals:**

- Add a reusable attached-client context that records host, port, ownership and attach timestamp for the current
  MCP server process.
- Centralize MCP protocol session creation behind a resolver so introspection, value-read, write and scenario
  tools stop creating unrelated raw sessions.
- Preserve explicit `host`/`port` parameters for callers that do not want the current attached endpoint.
- Return a bounded diagnostic with the failed phase (`attach`, `bootstrap`, `open_form`, `descriptor`, `write`) when
  an attached endpoint cannot be driven.
- Prove the route with offline tests and, when runtime preflight passes, a read-only out-of-band descriptor run.

**Non-Goals:**

- Do not change the low-level TestClient handshake bytes unless live evidence proves a bootstrap drift and the
  fix stays within the existing protocol templates.
- Do not add a new raw protocol claim or promote raw captures.
- Do not terminate an external TestClient during cleanup.
- Do not run business-data mutation evidence unless the existing write path has a reviewed safety/recovery plan.

## Decisions

### Attached Endpoint Context

`attach_test_client` should store a bounded in-process context for the MCP server session, for example
`AttachedTestClientContext(host, port, owns_process=false, attached=true, connected_at=...)`. The MCP response
should expose enough non-secret fields for consumers to know which endpoint is active.

Alternative considered: require every tool call to pass the returned host and port manually. That preserves the
current behavior and does not solve the review finding because the attach operation still has no durable effect
on the real replay-backed tools.

### Central Session Resolver

Add a small MCP-server helper such as `_testclient_session_factory(host, port, use_attached=None)` or
`_resolve_testclient_endpoint(...)` and route the scattered `TestClientSession(host=host, port=port)` call sites
through it. Default behavior should remain compatible:

- explicit `host` or `port` means use exactly the caller-provided endpoint;
- no explicit override and an attached context exists means use the attached context;
- no attached context means use the existing defaults.

The helper should validate that the attached endpoint is still listening before using it and return a structured
error for tool wrappers that need to fail closed.

Alternative considered: modify `TestClientSession` itself to discover an attached endpoint. That hides MCP state
inside a low-level package API and makes offline tests harder to reason about.

### Descriptor Diagnostics

The empty descriptor regression must not be reported as success. For attached endpoint calls, the descriptor path
should distinguish:

- endpoint disappeared before session open;
- bootstrap/open failed;
- form navigation failed;
- descriptor query succeeded but returned no elements.

Read-only descriptor evidence is sufficient for the live gate because it proves the formerly broken attach path.
Write tools get route-level offline coverage first; live mutation can be added only with existing recovery proof.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Out-of-band TestClient attach feeding `read_form_descriptor` and value-read/write session factories | Attach a listening endpoint, then run descriptor through the attached context; offline tests prove write/session factory routing | `qa_testclient_scenario`, `form_tree` or descriptor summary, bounded run log, pytest summary | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live preflight may report lab contention before starting or attaching 1C. |
| Delivery or runtime apply | Linux runtime preflight and externally owned TestClient cleanup boundary | Run preflight before any live attach/probe; stop only owned processes from the proof harness | `source_preflight`, retained cleanup summary | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | External clients are intentionally not killed by qa-mcp cleanup. |
| Business data mutation | Create/fill/save proof through an attached endpoint | Keep live mutation behind existing safe write/recovery policy; verify route offline unless a reviewed mutation manifest exists | offline pytest for route; optional `qa_testclient_bundle` with cleanup evidence if executed | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The card unblocks the route; live mutation remains higher risk without recovery evidence. |
| Windows-native verification | Windows host or COM launch path | No Windows launcher or host-agent behavior changes | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This Linux-native attach/session change does not modify Windows process launch or host-agent code. | Windows out-of-band clients still rely on explicit host/port or future host-agent evidence. |

## Risks / Trade-offs

- [Risk] A global attached context could surprise callers that expect defaults. -> Mitigation: preserve explicit
  `host`/`port` override and include active endpoint data in tool diagnostics.
- [Risk] The out-of-band client still fails during bootstrap because the real root cause is protocol drift. ->
  Mitigation: return a precise bootstrap/open diagnostic and keep the fix local to the failing phase.
- [Risk] Live mutation evidence could change business data. -> Mitigation: run read-only proof as the required
  live gate and require recovery evidence before optional mutation proof.
- [Risk] The MCP process is restarted between attach and tool calls. -> Mitigation: return a clear "no active
  attached endpoint" diagnostic and keep direct host/port calls supported.

## Migration Plan

1. Add the attached endpoint context and central session resolver.
2. Route descriptor, value-read, write and scenario session factories through the resolver.
3. Add focused offline tests for attach persistence, explicit override behavior, descriptor diagnostics and
   write/session factory routing.
4. Run OpenSpec validation and focused pytest.
5. Run Linux runtime preflight and a read-only out-of-band descriptor probe when safe; retain evidence under the
   ignored artifact root.

Rollback is removing the context/resolver and restoring direct `TestClientSession(host, port)` construction in the
MCP wrappers. No persisted user data or infobase migration is involved.

## Open Questions

- Whether live out-of-band descriptor failure is purely routing/context or a deeper bootstrap drift will be
  resolved during implementation by the retained descriptor proof.
