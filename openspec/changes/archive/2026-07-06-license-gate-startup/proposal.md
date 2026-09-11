## Why

The public qa-mcp delivery needs a **product license** — per-user, working ~2
weeks offline — and the user's decision (card 121) is to reuse the suite's proven
**provider startup license gate** rather than a bespoke trial. Four providers
(`help-/knowledge-/meta-/live-mcp`) already ship this gate; the root contract
(`docs/dev-mcp-suite-provider-startup-license-gates.md`) mandates component-local
implementation, and qa-mcp was explicitly deferred from the first wave. This
change adds the gate to qa-mcp.

It is the **self-contained, testable-without-a-server** first step: the gate runs
the native broker `ai1c-license check --component qa-mcp --json`, fails closed
unless allowed, and is **env-flagged OFF by default** (`QA_MCP_LICENSE_GATE`), so
the current free delivery is unaffected until the delivery + server side are
ready. It is COUPLED to card 122: an enforced gate in readable `.py` is a trivial
bypass (delete the `check` call), so the gate is built here OFF, compiled by card
122's Nuitka stage, and only turned ON in later changes.

This change touches **Python manager code** (the `main()` startup path) + tests;
it requires **no live 1C runtime and no license server** — the test matrix uses a
**fake broker**, per the root contract. The dev source keeps the gate readable
(`.py`); the IMAGE compiles it (card 122).

## What Changes

- Add a **startup license gate** at the top of `mcp_server.main()` (before
  `mcp.run()`): when enabled, run `ai1c-license check --component qa-mcp --json`
  (broker path + timeout configurable via env), parse the JSON, and **ALLOW only
  when ALL hold**: exit code `0`, `allowed: true`, status `licensed` **or**
  `offline_grace`, response schema + component match. On `offline_grace` → start
  but surface the grace (incl. the broker grace timestamp) in **diagnostic-safe**
  startup output.
- **Fail closed** (DENY → process exits non-zero with an actionable, diagnostic-safe
  message) on every deny case: non-zero exit, `allowed:false`, missing/unlaunchable
  broker, timeout, malformed JSON, unsupported schema, component mismatch, no lease,
  denied entitlement, expired lease/grace, invalid signature, unknown/revoked key,
  fingerprint mismatch.
- **Diagnostic safety:** never log keys, raw hardware ids, customer/1C/infobase/path
  data, traces, screenshots or credentials (root contract § Diagnostic Safety).
- **Env-flagged, OFF by default:** the gate runs only when `QA_MCP_LICENSE_GATE` is
  set (e.g. `=1`); unset → current behavior, no broker call. Broker path/timeout are
  configurable (e.g. `QA_MCP_LICENSE_BROKER` / `QA_MCP_LICENSE_TIMEOUT`).
- **Tests** cover the contract's required matrix with a **fake broker**: allowed /
  offline_grace / denied / malformed / missing-broker / timeout.

## Capabilities

### New Capabilities

- `qa-mcp-license-gate`: qa-mcp gates its own MCP startup on the native suite
  license broker — ALLOW only on exit0 + `allowed` + `licensed`/`offline_grace`,
  fail-closed otherwise, `offline_grace` surfaced diagnostic-safely — and the gate
  is env-flagged OFF by default so the free delivery is unaffected until enforced.

### Modified Capabilities

- none

## Impact

- **Python manager code:** `src/qa_mcp/mcp_server.py` (`main()` startup gate + a
  small license-check helper module). New env vars: `QA_MCP_LICENSE_GATE` (default
  off), broker path + timeout overrides.
- **Tests:** a fake-broker fixture + the 6-case contract matrix.
- **No live dependency:** no server, no broker binary required for tests; the
  current delivery is unchanged with the flag off.
- **Coupled to card 122:** this gate is enforceable only once compiled. **Out of
  scope here:** shipping the broker binary (`license-broker-in-image`), activation
  + turning the gate ON (`license-activation-bootstrap`), and the server-side config
  (root/`license/` coordination).
