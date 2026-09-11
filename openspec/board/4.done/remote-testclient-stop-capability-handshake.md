# Preserve host-agent lifecycle-stop capabilities in remote handshake

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived; independent review passed; published

## Source
- Follow-up from independent review cycle 5 of
  `openspec/board/4.done/remote-testclient-owned-lifecycle.md`.
- Non-blocking major finding R1:
  `RemoteAgentBackend.handshake()` drops advertised `/version` capabilities
  before `host_agent_testclient_lifecycle_stop_supported()` can evaluate them.

## Summary
The remote TestClient stop safety path is correct for the current
`0.1.10-testclient-lifecycle-handle` host-agent and for fail-closed refusal of
the legacy `0.1.9-testclient-owned-lifecycle` PID-only route. The remaining
gap is forward compatibility: a future protocol-compatible host-agent can
advertise explicit lifecycle-handle stop support, but the Python handshake
currently reconstructs a sanitized result without the `capabilities` field, so
that future capable host-agent would still be refused.

## Acceptance
- [x] `RemoteAgentBackend.handshake()` preserves a bounded, validated
  capabilities field from `/version` when the host-agent returns either a list
  of capability names or a mapping whose values are explicit booleans.
- [x] `host_agent_testclient_lifecycle_stop_supported()` treats the current
  lifecycle-stop version as supported, treats an explicit capability as
  supported for protocol-compatible future versions, and does not treat
  arbitrary truthy capability values as support.
- [x] `RemoteAgentBackend.stop_test_client()` posts `/testclient/stop` for a
  protocol-compatible future host-agent that advertises
  `testclient-lifecycle-handle-stop`.
- [x] `RemoteAgentBackend.stop_test_client()` continues to refuse
  `0.1.9-testclient-owned-lifecycle` before `/testclient/stop` when no
  lifecycle-stop capability is advertised.
- [x] Offline regression tests cover both the direct helper and the real
  `_json()` -> `handshake()` -> `stop_test_client()` path.

## Change Set
- `preserve-remote-testclient-stop-capability-handshake`:
  `openspec/changes/archive/2026-07-31-preserve-remote-testclient-stop-capability-handshake/`

## Change 1: `preserve-remote-testclient-stop-capability-handshake`

### Why
Remote lifecycle stop support can be advertised by future host-agents through
`/version.capabilities`, but qa-mcp currently drops that field before the stop
support helper can evaluate it.

### Goal
Preserve bounded lifecycle-stop capabilities through the remote handshake and
use them to route remote TestClient stop only for explicitly capable
protocol-compatible host-agents.

### Scope
- `RemoteAgentBackend.handshake()` capability normalization.
- `host_agent_testclient_lifecycle_stop_supported()` capability checks.
- `RemoteAgentBackend.stop_test_client()` future-capable and legacy-refusal
  behavior.
- Focused offline Python regression tests.

### Acceptance
- As in the card Acceptance.

### Depends On
- Published lifecycle card:
  `openspec/board/4.done/remote-testclient-owned-lifecycle.md`.

### Related
- `openspec/changes/archive/2026-07-31-preserve-remote-testclient-stop-capability-handshake/`
- Python backend:
  `src/qa_mcp/protocol/display_backend.py`
- Existing tests:
  `tests/test_display_backend.py`

## Verify
- RED focused Python:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py::test_testclient_lifecycle_stop_support_is_capability_specific tests/test_display_backend.py::test_remote_handshake_preserves_lifecycle_stop_capability_list tests/test_display_backend.py::test_remote_handshake_preserves_boolean_capability_mapping tests/test_display_backend.py::test_remote_testclient_stop_accepts_future_lifecycle_capability_from_handshake tests/test_display_backend.py::test_remote_testclient_stop_rejects_truthy_future_lifecycle_capability -q`
  -> failed before implementation with truthy mapping accepted, missing
  `capabilities` in `handshake()`, and future-capable stop still refused.
- GREEN focused Python:
  same command -> 5 passed.
- GREEN display backend:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -q`
  -> 50 passed.
- GREEN full Python:
  `uv run --with pytest --with pyyaml pytest -q` -> 878 passed.
- Compile:
  `python3 -m compileall -q src/qa_mcp/protocol/display_backend.py` -> passed.
- OpenSpec:
  `openspec validate preserve-remote-testclient-stop-capability-handshake --type change --strict`
  -> passed; `openspec validate --all --strict` -> 20 passed, 0 failed.
- Post-archive OpenSpec:
  `openspec validate --all --strict` -> 19 passed, 0 failed.
- Whitespace:
  `git diff --check` -> passed.

## Archive
- `openspec/changes/archive/2026-07-31-preserve-remote-testclient-stop-capability-handshake/`

## Related
- Published lifecycle card:
  `openspec/board/4.done/remote-testclient-owned-lifecycle.md`
- Review verdict:
  `.runtime/changerail/reviews/remote-testclient-owned-lifecycle.json`
- Python backend:
  `src/qa_mcp/protocol/display_backend.py`
- Existing tests:
  `tests/test_display_backend.py`

## Result
Published in the scoped ChangeRail delivery commit
`fix(testclient): preserve remote stop capabilities`; push pending to
`origin/main`.

## Next
- none.

## Log
- 2026-07-31T09:35:00Z card created after publishing the
  `remote-testclient-owned-lifecycle` delivery with review cycle 5 `GO`.
- 2026-07-31T10:12:00Z `$changerail-ff`: decomposed to one apply-ready change,
  `preserve-remote-testclient-stop-capability-handshake`; card moved to
  `2.todo`.
- 2026-07-31T10:30:00Z `$changerail-do`: implemented capability normalization,
  strict boolean capability support checks, future-capable stop routing, and
  legacy/falsy refusal regressions; synced main spec and completed offline
  verification.
- 2026-07-31T10:35:00Z archived OpenSpec change as
  `openspec/changes/archive/2026-07-31-preserve-remote-testclient-stop-capability-handshake/`.
- 2026-07-31T10:27:31Z independent `$changerail-review` cycle 1 returned
  `go` with 5/5 acceptance criteria passed and 0 findings.
- 2026-07-31T10:45:00Z `$changerail-pub`: committed scoped card delivery with
  message `fix(testclient): preserve remote stop capabilities` and prepared
  push to `origin/main`.
