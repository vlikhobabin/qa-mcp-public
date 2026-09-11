## 1. Installer Network Scope

- [x] 1.1 Change `host-agent/install-windows-host-agent.ps1` defaults so a normal install binds locally or creates a firewall rule with an explicit remote-address scope.
- [x] 1.2 Add or preserve an explicit operator option for Docker Desktop/non-loopback routing, with visible warning text when broad exposure is requested.
- [x] 1.3 Ensure the scheduled-task action no longer embeds the token value in its command line.

## 2. Host-Agent Auth Hardening

- [x] 2.1 Add a protected token-file or environment-token load path in the Go server configuration.
- [x] 2.2 Use constant-time token comparison in the auth middleware.
- [x] 2.3 Require auth for desktop-control endpoints and sensitive `/version` or detailed health data; keep any unauthenticated health response minimal.
- [x] 2.4 Reject non-allowlisted browser `Origin` headers before action execution.
- [x] 2.5 Add a lightweight request rate limit for repeated unauthenticated or wrong-token attempts.

## 3. Documentation And Verification

- [x] 3.1 Document secure install, Docker Desktop routing, token-file storage and residual command-line credential risks in `delivery/windows-agent-runbook.md`.
- [x] 3.2 Add or update focused Go tests for accepted token, wrong token, missing token, hostile origin and public status leakage behavior.
- [x] 3.3 Run `go test ./...` from `host-agent/`.
- [x] 3.4 Run `openspec validate host-agent-network-hardening --strict`.
