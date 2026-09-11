## 1. Host-Agent Diagnostics

- [x] 1.1 Add a secret-safe active-process summary to valid
  `POST /path/infobase` responses.
- [x] 1.2 Detect only 1C client process names and path matches when the host
  can inspect process metadata.
- [x] 1.3 Return an explicit unavailable signal when process metadata cannot be
  inspected.
- [x] 1.4 Preserve existing authentication, path validation, marker-only, and
  no-browsing behavior.

## 2. Tests

- [x] 2.1 Add host-agent tests for matched 1C process metadata, unmatched 1C
  processes, unavailable process metadata, and secret redaction.
- [x] 2.2 Keep existing path-probe auth and invalid-request tests green.

## 3. Verification

- [x] 3.1 Run `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent`.
- [x] 3.2 Run `go test ./...` in `host-agent/windows-display-agent`.
- [x] 3.3 Run read-only Windows endpoint evidence when
  `historical-user@192.0.2.205` / `HISTORICAL-LAB-HOST` is reachable, or record the exact
  unavailable condition.
- [x] 3.4 Run `openspec validate host-agent-infobase-active-process-probe --strict`.
- [x] 3.5 Run `openspec validate qa-mcp-windows-host-agent-security --strict`.
- [x] 3.6 Run `openspec validate --all --strict`.
- [x] 3.7 Run `git diff --check`.

Evidence: focused and full Go tests passed; Windows SSH reached
`historical-user@192.0.2.205` / `HISTORICAL-LAB-HOST`, temporary loopback host-agent
`POST /path/infobase` confirmed `C:\1C_BASES\demo10413\1Cv8.1CD`, returned
`active_processes.status="available"` with zero matching 1C processes at the
time of the probe, and redaction checks confirmed no raw path, token, command
line or process id in the response. Sanitized ignored evidence:
`.runtime/changerail/evidence/host-agent-active-process-demo10413-20260728T212337Z.json`.
