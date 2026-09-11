## Context

`mcp_server.main()` (line ~2851) selects transport and calls `mcp.run()`; it is the
single startup choke point. Four suite providers already ship the
provider-startup-gate against `ai1c-license check --component <name> --json` per the
root contract (`docs/dev-mcp-suite-provider-startup-license-gates.md`); qa-mcp
copies that pattern. The broker has no offline self-trial — `offline_grace` is the
window AFTER a one-time online activation.

## Goals / Non-Goals

- **Goal:** a contract-correct, fail-closed startup gate, OFF by default, fully
  testable with a fake broker (no server, no real binary).
- **Goal:** zero impact on the current free delivery when the flag is unset.
- **Non-Goal:** shipping the broker binary, the container fingerprint/lease wiring,
  activation, or turning the gate ON (later changes).
- **Non-Goal:** server-side config (root/`license/` coordination).

## Decisions

- **D1 — Gate at the top of `main()`.** Before transport selection / `mcp.run()`.
  If `QA_MCP_LICENSE_GATE` is falsy/unset → return immediately (no broker call).
- **D2 — A dedicated helper module (`license_gate.py`).** Mirror the 4 shipped
  providers: `qa_mcp/license_gate.py` exposes `check_qa_mcp_startup_license(*,
  executable, timeout_seconds, runner=None)` with an **injectable `runner`**
  (`BrokerRunner`) so the contract matrix tests pass a fake broker (a
  `CompletedProcess` or an exception) with no real binary / no subprocess. (Chosen
  over a separate `evaluate(payload, exit_code)` split — the DI-runner is the proven
  suite pattern and equally testable.) Suite-consistent name `license_gate.py`
  (not `licensing.py`) for cross-provider grep parity.
- **D3 — ALLOW predicate (all required).** exit `0` AND `allowed is true` AND
  status in {`licensed`,`offline_grace`} AND response schema id matches AND
  component == `qa-mcp`. Anything else → DENY.
- **D4 — Fail-closed = exit non-zero, no serve.** Raise/`sys.exit` with a stable,
  diagnostic-safe message naming the failure class (not the raw broker payload).
- **D5 — Diagnostic safety.** Surface only: allowed/denied, status, a stable reason
  code, and (for grace) the grace timestamp. Never echo keys, hardware ids,
  customer/1C/infobase/path data, traces, screenshots, credentials, or the raw JSON.
- **D6 — Config via env.** `QA_MCP_LICENSE_GATE` (enable), `QA_MCP_LICENSE_BROKER`
  (path, default `ai1c-license` on PATH), `QA_MCP_LICENSE_TIMEOUT` (seconds).
- **D7 — Timeout + missing broker both DENY.** A subprocess timeout or a
  missing/unlaunchable broker is a deny case (fail closed), not a soft-allow.

## Risks / Trade-offs

- **Bypassability in `.py`:** acknowledged — teeth come from card 122's compile.
  Build OFF now; enforce only after compiled.
- **Contract drift vs the 4 providers:** mitigated by mirroring the root contract's
  exact ALLOW/DENY matrix and the documented exit codes.
- **Over-broad diagnostics leaking data:** mitigated by D5 + a test asserting the
  denied/grace messages contain none of the forbidden tokens.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager code | `main()` gate + `licensing.evaluate` | contract-correct allow/deny; OFF by default | offline `pytest`: the 6-case fake-broker matrix passes | CI / local run log | planned | qa-mcp | — |
| Diagnostic safety | grace/deny startup output | no keys/hw-id/customer/path/creds | a test asserts forbidden tokens absent from messages | CI / local run log | planned | qa-mcp | — |
| Free-delivery parity | flag unset | no broker call, current behavior | a test asserts startup with the flag unset makes no broker call | CI / local run log | planned | qa-mcp | — |
| Live licensing | real broker + server | — | — | — | n/a | qa-mcp | no server/binary in this change; activation + ON are later changes |

Residual risk: enforceability depends on compiling the **gate-bearing** modules
(`mcp_server.py` + `license_gate.py`) — which the card-122 `nuitka-protocol-build-stage`
does NOT do (it compiles only `protocol/`). Compiling the non-protocol modules is
card 123 D2's scope; sequence it before turning the gate ON
(`license-activation-bootstrap`). Until then the gate is OFF, so there is no
premature, bypassable enforcement.
