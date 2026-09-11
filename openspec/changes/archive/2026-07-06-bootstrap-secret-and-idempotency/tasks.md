## 1. Sensitive Launch Helper Cleanup

- [x] 1.1 Update `delivery/bootstrap.ps1` so the TestClient launch helper is created with user-only ACLs.
- [x] 1.2 Ensure the launch helper is removed after the TestClient launch attempt succeeds or fails.
- [x] 1.3 Delete or replace the `qa-mcp-testclient` scheduled task so it cannot rerun a stale password-bearing helper.
- [x] 1.4 Add tests proving the script contains cleanup for `launch-testclient.ps1` and does not leave the password helper as durable state.

## 2. Rerun Idempotency

- [x] 2.1 Add a pre-launch listener check for `ClientPort`.
- [x] 2.2 Fail with a clear stale-client diagnostic when a pre-existing listener cannot be proven to belong to the intended bootstrap run.
- [x] 2.3 Replace stale `qa-mcp-testclient` task state before creating the new task.
- [x] 2.4 Add tests proving an existing listener path cannot be counted as successful launch of a new infobase.

## 3. Window Ownership

- [x] 3.1 Capture the process id from the launched TestClient when the scheduled task starts it.
- [x] 3.2 Prefer the captured process id when deriving `WindowTitle` from host-agent `window_list`.
- [x] 3.3 Keep an explicit warning or failure when automatic window derivation remains ambiguous.

## 4. Verification

- [x] 4.1 Run focused bootstrap tests covering password cleanup, scheduled-task replacement and stale-listener diagnostics.
- [x] 4.2 Run `openspec validate bootstrap-secret-and-idempotency --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 When a Windows tester environment is available, retain a smoke log under `.artifacts/openspec/bootstrap-secret-and-idempotency/<run-id>/` showing no plaintext launch helper remains after success and a second-infobase rerun fails loudly or replaces the prior TestClient. Linux delivery retained an environment-gap note because no Windows tester session was available in this run.
