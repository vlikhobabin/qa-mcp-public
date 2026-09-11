## 1. Implementation

- [x] 1.1 Add bounded capability normalization for
  `RemoteAgentBackend.handshake()` list and boolean-mapping `/version` payloads.
- [x] 1.2 Keep `host_agent_testclient_lifecycle_stop_supported()` exact for the
  current lifecycle-stop version and explicit lifecycle-stop capability only.
- [x] 1.3 Ensure `RemoteAgentBackend.stop_test_client()` can post
  `/testclient/stop` for a protocol-compatible future host-agent when the
  handshake advertises `testclient-lifecycle-handle-stop`.
- [x] 1.4 Ensure `RemoteAgentBackend.stop_test_client()` still refuses
  `0.1.9-testclient-owned-lifecycle` before `/testclient/stop` when the
  capability is absent or malformed.

## 2. Verification

- [x] 2.1 Add offline regression tests covering list capabilities, boolean
  mapping capabilities, and non-boolean truthy mapping values.
- [x] 2.2 Add offline regression tests for the real `_json()` -> `handshake()`
  -> `stop_test_client()` path for future-capable and legacy-unsupported
  host-agent responses.
- [x] 2.3 Run focused Python tests:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -q`.
- [x] 2.4 Run strict OpenSpec validation and whitespace checks:
  `openspec validate preserve-remote-testclient-stop-capability-handshake --type change --strict`,
  `openspec validate --all --strict`, and `git diff --check`.
