## 1. Session setup cleanup

- [x] 1.1 Wrap `NativeWriteSession.__enter__` setup replay so a created socket is closed on setup failure.
- [x] 1.2 Preserve the original setup exception and clear failed socket/session state after cleanup.

## 2. Send timeout hygiene

- [x] 2.1 Apply a send-appropriate timeout before each outbound `sendall`.
- [x] 2.2 Restore receive timeout behavior for response draining after sends.
- [x] 2.3 Map `socket.timeout` raised during send to a distinct send-timeout reason instead of divergence.

## 3. Runtime process ownership

- [x] 3.1 Add an ownership/identity guard before `stop_test_client(pid)` kills a process group.
- [x] 3.2 Return a structured refusal for stale, unrelated or unrecognized pids.
- [x] 3.3 Preserve existing cleanup for recorded or recognizable owned TestClient runtime processes.

## 4. Tests

- [x] 4.1 Add fake-socket tests proving setup failure closes the socket.
- [x] 4.2 Add slow-send tests proving send timeouts are classified distinctly.
- [x] 4.3 Add process-ownership tests proving an unrelated pid is refused without `killpg`.

## 5. Verification

- [x] 5.1 Run focused lifecycle/session tests.
- [x] 5.2 Run `uv run pytest -q`.
- [x] 5.3 Run `openspec validate socket-timeout-hygiene --strict`.
- [x] 5.4 Run `git diff --check -- openspec/changes/socket-timeout-hygiene src tests`.

## 6. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Native session lifecycle | `NativeWriteSession.__enter__` setup replay failure | fake socket that raises during setup | `uv run pytest -q tests/test_native_write.py tests/test_lifecycle.py` (85 passed), `uv run pytest -q` (624 passed) | `tests/test_native_write.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: setup cleanup is local to failed session startup |
| Socket send timeout | outbound frames in native write/session calls | fake socket with slow-send timeout | offline unit test proves `send_timeout` / `send_timeout_at`, not `real_divergence_at` | `tests/test_native_write.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: external callers may compare old reason text |
| Runtime cleanup ownership | `stop_test_client(pid)` process-group teardown | fake `/proc` or monkeypatched ownership probe | offline unit test proves non-owned/non-TestClient pid refusal without `_terminate_group`; recognized `1cv8` + `Xvfb` still clean up | `tests/test_lifecycle.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: stateless pid ownership remains conservative by design |
| Business data / posting | no runtime/business data surface | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | no business command, posting, import/export, or object write is introduced | No residual risk; no business-data surface is touched |
