## Why

Healthy model-B setups currently require several manual probes to distinguish
real failures from false negatives. Users can see "unauthorized",
`open-link-required`, or a nominal attach while the client is stuck at a login
dialog, and none of those states gives a single actionable setup verdict.

## What Changes

- Add one `qa_mcp_doctor` diagnostic surface as both an MCP tool and CLI entry
  point that returns a secret-safe pass/fail chain for proxy auth, host-agent
  HTTP reachability, container-to-host route, platform discovery, TestClient
  TPort reachability, open-link-free TestClient smoke, login-dialog state, and
  the existing COMConnector doctor path.
- Make auth failures distinguish a missing bearer-token environment variable
  from a supplied-but-rejected token by returning `token_env_present:false`
  without exposing token values.
- Add a low-level "connected to TestClient" smoke that does not require
  `open_link`, and make `get_window_list_testclient` guidance point callers to
  the smoke or to explicit `open_link` examples when they need form-level reads.
- Report effective user and login/access-dialog stuck state when it is
  queryable from the attached TestClient, so a wrong `-User` does not look like
  a successful attach.
- Update focused tests and troubleshooting docs for the end-to-end doctor and
  the known model-B false-negative cases.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: add the doctor MCP/CLI result contract,
  open-link-free TestClient smoke, structured auth hint, and attach/user-state
  diagnostics.
- `qa-mcp-suite-container-delivery`: add the model-B setup diagnostic contract
  for proxy auth and host-agent HTTP/container reachability.
- `qa-mcp-runtime-configuration`: document and parse the non-secret doctor
  configuration inputs, including bearer-token presence without exposing token
  values.

## Impact

- Touches Python manager/MCP code, runtime configuration, tests, docs, and
  OpenSpec artifacts.
- Uses the existing Windows host-agent and COM doctor contracts rather than
  changing host-agent authentication or COM execution semantics.
- Requires only offline tests in this Linux workspace for implementation
  verification; live Windows/1C evidence is recorded as a model-B runtime
  verification gap unless an operator-provided Windows host is available.
