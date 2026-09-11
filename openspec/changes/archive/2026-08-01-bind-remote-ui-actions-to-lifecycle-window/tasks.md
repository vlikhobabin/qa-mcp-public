## 1. Preflight and RED contracts

- [x] 1.1 Record the runtime-verification preflight rows from `design.md`, including clean component scope, authorized Windows host identity/session readiness, screenshot route, ignored evidence root, and explicit no-infobase-write/no-protocol-capture boundary.
- [x] 1.2 Add focused Python RED tests proving active launch/attach `client_target` propagation for screenshot, keys, type, click, and visible cells; explicit-selector precedence; capability fail-closed behavior; and typed session-error preservation.
- [x] 1.3 Add focused Go RED tests proving lifecycle/PID/TPort validation, empty-title target acceptance, weak/wildcard/unrelated-foreground refusal before driver calls, explicit-selector precedence, and distinct locked/disconnected/non-interactive errors.

## 2. Python lifecycle-target propagation

- [x] 2.1 Extend remote launch and host-agent-assisted attach results plus `_AttachedTestClientContext` with a bounded non-HWND `client_target`, preserving `owns_process=false` for attach-only clients.
- [x] 2.2 Bind remote display backend instances to the active target and send it on implicit `capture_screenshot`, `send_keys`, `type_text`, `click`, and visible-list-cell requests while preserving explicit selector precedence.
- [x] 2.3 Preserve/validate the `testclient-window-target` handshake capability and return typed MCP errors without retrying an unsafe legacy or weak target.

## 3. Windows host-agent target and session safety

- [x] 3.1 Add the bounded `client_target` request/status contract, advertise the new capability/version, and validate owned lifecycle id plus PID/TPort or attach-only PID/TPort before display dispatch.
- [x] 3.2 Resolve process-owned `V8TopLevelFrame*` windows even when the caption is empty, remove implicit foreground/generic-window fallback, reject wildcard/ambiguous inputs, and retain explicit-selector precedence.
- [x] 3.3 Add an injectable Windows desktop-session probe and structured `desktop-session-locked`, `desktop-session-disconnected`, and `desktop-session-noninteractive` mappings that stop before screenshot/input/UIA driver calls.

## 4. Durable documentation

- [x] 4.1 Update the host-agent and MCP tool documentation for launch/attach target output, implicit target inheritance, explicit selector precedence, capability requirements, typed session diagnostics, and the no-foreground-fallback safety rule.
- [x] 4.2 Record that protocol corpus/evidence-index updates are not applicable because the change makes no TestClient wire claim; keep all Windows screenshots, identities, binaries, payloads, and logs under ignored `.runtime/` paths.

## 5. Verification and retained evidence

- [x] 5.1 Run the focused Python endpoint/backend tests and explain why they observe request propagation/refusal rather than merely restating implementation data.
- [x] 5.2 Run `go test -count=1 ./...` under `host-agent/windows-display-agent` and compile its Windows test binary with `GOOS=windows GOARCH=amd64`.
- [x] 5.3 Run the full offline Python coverage gate: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`.
- [x] 5.4 After a bounded Windows preflight, run the source-bound host-agent integration proof for empty-title exact targeting, explicit override, unrelated-foreground isolation, the five display routes, typed session states, and cleanup; retain only sanitized outcome JSON under `.runtime/changerail/evidence/bind-remote-ui-actions-to-lifecycle-window/`.
- [x] 5.5 Run `openspec validate bind-remote-ui-actions-to-lifecycle-window --strict`, `openspec validate --all --strict`, `git diff --check`, and review the final diff/evidence boundary before sync and archive.

## 6. Independent-review rescue

- [x] 6.1 Reproduce review findings R1/R2 with branch-sensitive RED tests for the implicit visible-list diagnostic, wildcard configuration, and active contexts whose client target is missing or invalid.
- [x] 6.2 Remove the synthesized generic visible-list selector and require a validated lifecycle/client target before every implicit display POST while preserving explicit-selector precedence and no-active-context port fallback.
- [x] 6.3 Rerun the focused rescue suite, complete display/MCP regression, offline coverage gate, Go suite, Windows cross-compile, strict OpenSpec validation, diff check, and explicit untracked whitespace scan.
