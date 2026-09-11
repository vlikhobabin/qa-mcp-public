## Context

The Python remote display backend currently sends a configured `window` and `client_port`. The Windows host-agent resolves the port to a PID, but blank/weak targeting can still reach a generic 1C-window or foreground-window heuristic, and empty-title windows are omitted from the enumerated candidate set. The MCP server separately remembers the active TestClient attachment, including an opaque lifecycle handle for provider-owned launches, but display backend instances do not consume that state.

This change crosses the Python MCP endpoint, Python host-agent client, Go host-agent request/identity boundary, Win32 window resolution, and Windows runtime evidence. It changes no 1C metadata or BSL and makes no new TestClient wire-protocol claim. Capture ids, frame ranges, dynamic fields, normalized hashes, and replay strategy are therefore `N/A`; the proof source is the typed Python/Go contract plus Windows-native host-agent integration evidence.

Constraints:

- Explicit non-empty, non-wildcard window selectors remain an intentional operator override.
- Implicit targeting while an active TestClient context exists must never fall back to the foreground application or to an unrelated 1C process.
- Launch ownership and stop authorization remain separate from display targeting: an out-of-band attached client may be a valid display target but is never inferred to be provider-owned.
- Runtime evidence must contain only sanitized booleans, counts, reason codes, version/capability facts, and test outcomes. Raw screenshots, HWNDs, PIDs, titles, credentials, host-agent logs, and infobase contents remain ignored and unretained.

## Goals / Non-Goals

**Goals:**

- Derive a bounded `client_target` from the active remote launch or attach result and send it on implicit screenshot, key, text, click, and visible-cell requests.
- Validate the target on the host by matching its lifecycle id (when owned), PID, listening TPort, and current process-owned 1C window before any display operation.
- Resolve visible empty-title `V8TopLevelFrame*` windows without caption matching.
- Keep explicit selector precedence while treating blank/wildcard selectors as implicit targeting.
- Return stable, typed locked, disconnected, and non-interactive desktop diagnostics through MCP results.
- Prove fail-closed behavior and the Windows path without retaining sensitive desktop artifacts.

**Non-Goals:**

- Changing native TestManager/TestClient wire frames or promoting protocol corpus mappings.
- Granting process ownership or stop authority to attach-only clients.
- Adding generic arbitrary-window automation, OCR, new UIA semantics, or business-data mutation.
- Committing screenshots, raw window/process identities, or host-agent logs.

## Decisions

### 1. Use a structured client target, not a caption or caller-supplied HWND

Remote launch and host-agent-assisted attach results will expose a bounded `client_target` containing `kind`, PID, TPort, and the opaque lifecycle id when one exists. The Python active-attachment record will retain that object and inject it into remote display backend instances. The host-agent will re-resolve the live listener/window and validate every supplied field; it will not trust a raw HWND from the caller.

This reuses the lifecycle identity for owned launches while allowing a non-owning attach target. Passing only a caption was rejected because empty titles are valid. Passing an HWND was rejected because handles are ephemeral, leak host detail, and are unsafe across window/process reuse.

### 2. Define strict target precedence and eliminate implicit foreground fallback

For display endpoints the order is:

1. a caller-supplied explicit selector other than blank or wildcard;
2. the active `client_target` validated by lifecycle/PID/port;
3. the existing `client_port` resolution only when no active target is available;
4. typed refusal.

The host-agent will not select the OS foreground window when these inputs cannot be resolved. Empty-title windows remain enumerable for internal PID/class matching. Explicit selectors continue to win because they are direct operator intent; wildcard/empty selectors do not count as explicit intent.

### 3. Make lifecycle-window targeting capability-gated

The host-agent version will advance and `/version` will advertise a `testclient-window-target` capability. Python will preserve the capability advertisement and require it before sending an implicit active `client_target`. A legacy host-agent may still serve an explicit selector, but it cannot silently downgrade an active lifecycle-bound request to its older heuristic.

This additive capability gate was chosen over exact-version authorization so future protocol-compatible host-agents can implement the same safety contract without another hard-coded version exception.

### 4. Resolve owned and attach-only targets differently without conflating authority

For an owned launch, the host-agent lifecycle store must match lifecycle id, PID, and TPort and must reject finalized/stale/mismatched records. For attach-only use, authenticated `/testclient/status` will resolve the local TPort to a PID and a visible process-owned 1C window, then return a non-owning `client_target`; subsequent display requests re-check the PID/port binding. Neither status nor target resolution creates a terminate callback or changes `owns_process`.

### 5. Surface typed desktop-session diagnostics before action

The Windows driver boundary will classify the current interactive desktop as active, locked, disconnected, or non-interactive through an injectable session probe. Every screenshot/input/visible-cell route will run the probe before the display primitive. Non-active states map to distinct structured error codes and do not call focus, input, screenshot, or UIA operations. Tests will inject each state; Windows-native verification will exercise the available integration path and record unsupported real-state transitions honestly rather than collapsing them into a generic conflict.

### 6. Keep verification evidence layered and sanitized

Offline Python tests prove active-target propagation, explicit precedence, capability refusal, and MCP diagnostic preservation. Go tests prove request validation, lifecycle/PID/port matching, no driver call on refusal, empty-title target metadata handling, and typed session errors. Windows cross-compile and native Go execution prove the Windows build/runtime path. A bounded Windows host-agent proof records only booleans/reason codes for exact-target screenshot/key/visible-cell behavior and cleanup; generated PNGs/logs stay under ignored `.runtime/` paths and are deleted or left ignored.

## Verification Preflight Matrix

| Check | State / planning output | Evidence / owner |
| --- | --- | --- |
| Trace/profile/proxy | `not_applicable`: component-local implementation does not depend on suite trace or proxy routing. | N/A; residual risk is limited to missing retrospective telemetry, owner `qa-mcp`. |
| `config-mcp` readiness | `not_applicable`: no 1C source/XML changes. | N/A; no import plan, owner `qa-mcp`. |
| `bsl-mcp` readiness | `not_applicable`: no BSL changes. | N/A; no BSL diagnostics, owner `qa-mcp`. |
| QA TestClient | `required`: focused Python/Go contracts plus Windows host-agent integration against the authorized Windows target. | `.runtime/changerail/evidence/bind-remote-ui-actions-to-lifecycle-window/`, owner `/opt/ai-dev-suite-for-1c/qa-mcp`. |
| Live/admin connectivity | `required` only for the Windows host-agent proof; no infobase write/apply is authorized. Confirm host identity and interactive-session state before the proof. | Sanitized preflight/result JSON under the ignored evidence root; owner `qa-mcp`/authorized Windows lab. |
| Fixture probes | `required`: one owned or attached TestClient/Windows fixture with an empty-title target, plus fake-driver cases for unrelated-foreground refusal. | Ignored Windows integration summary and Go test output, owner `qa-mcp`. |
| Role matrix readiness | `not_applicable`: no 1C business-role or permission behavior changes. | N/A; technical desktop session is not business-role proof. |
| Screenshot readiness | `required`: prove PNG success only as sanitized booleans/size presence; do not retain the image in reviewed payload. | Ignored evidence root, owner `qa-mcp`. |

## 1C Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delivery_or_runtime_apply | Windows host-agent display bridge and active remote TestClient attachment | Exact-target scenario covering screenshot, keys, text, click, visible cells, empty title, explicit override, unrelated foreground, and session-state refusals | Focused Python/Go tests, Windows cross-compile, Windows-native integration summary, cleanup audit | `.runtime/changerail/evidence/bind-remote-ui-actions-to-lifecycle-window/` | required | N/A | Real locked/disconnected transitions may require an accepted typed-probe fallback if the authorized session cannot be safely transitioned. | `/opt/ai-dev-suite-for-1c/qa-mcp` |

## Risks / Trade-offs

- [Risk] A legacy host-agent ignores `client_target` and uses a weak heuristic. → Python capability-gates implicit active-target requests and fails closed before the display call.
- [Risk] PID or window handles are reused after attach. → Re-check listener PID/port and process-owned window on each request; owned targets additionally require the opaque lifecycle id.
- [Risk] Session-state APIs differ across Windows editions or service contexts. → Isolate the probe, retain typed unknown/non-interactive failure, and cover mappings with Windows-native tests.
- [Risk] Explicit selectors can intentionally target a window outside the active TestClient. → Preserve them as explicit operator authority, but never treat blank/wildcard selectors as explicit.
- [Risk] Stronger refusal behavior breaks callers that relied on foreground fallback. → Document the requirement to launch/attach first or supply an explicit selector; keep protocol-compatible explicit-window calls available.

## Migration Plan

1. Add RED Python and Go tests for target propagation/resolution, empty titles, refusals, and session errors.
2. Implement the host-agent capability, target validation, session probe, and Python active-target propagation.
3. Update durable tool/host-agent documentation and build the Windows artifact in ignored runtime state.
4. Run offline suites, cross-compile, preflight the authorized Windows target, run the bounded integration proof, and verify cleanup.
5. Rollback by reverting the Python/host-agent pair together. If only Python is upgraded, capability gating refuses unsafe implicit requests; if only the host-agent is upgraded, older Python continues using the existing port/explicit-window surface.

## Open Questions

- None. Any unavailable Windows target or unsafe real session transition is a recorded runtime gap, not permission to weaken the target contract.
