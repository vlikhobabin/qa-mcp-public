## Context

The host-agent exists so containerized qa-mcp code can ask a Windows desktop session to type, click and capture screenshots. That makes its HTTP boundary privileged even though the implementation is intentionally small. The install script must therefore avoid broad network exposure by default, and the agent must not leak enough unauthenticated metadata to help discover or target the logged-in session.

## Design

Use fail-closed defaults in both the installer and the Go server:

- Default `BindAddress` to loopback. When an operator deliberately chooses a non-loopback bind, require an explicit `RemoteAddress`/subnet for the firewall rule and make the unsafe choice visible in the install output.
- Store the agent token in a protected file under the host-agent program-data directory, or read it from an environment variable. The scheduled task should pass only a token-file path or rely on a protected environment source, never `-token <secret>`.
- Extend the Go config with a token-file path while preserving the existing token input as a direct/manual path for tests and non-service launches.
- Validate bearer tokens with a constant-time comparison after checking that both sides are non-empty.
- Route `/type`, `/send_keys`, `/click`, `/screenshot`, `/version` and detailed health/status data through the same auth middleware. A minimal unauthenticated health probe is allowed only when it contains no SHA, foreground window, HWND, token or session details.
- Reject non-empty browser `Origin` headers unless they match an explicit allowlist. API clients without `Origin` continue to work.
- Add a lightweight per-remote rate limiter to slow repeated unauthenticated or wrong-token attempts without adding an external dependency.
- Update `delivery/windows-agent-runbook.md` with the network model, Docker Desktop routing choice, token-file behavior and residual process-list risks from other 1C launch credentials.

## Verification

This is not a 1C runtime behavior change. Live TestClient proof, metadata apply, role checks and protocol capture evidence are not applicable. Verification is:

- Go unit tests for auth success/failure, constant-time-token path coverage through behavior, hostile-origin rejection, minimal unauthenticated health/version behavior and installer command/token handling where script text can be inspected.
- Static inspection of `host-agent/install-windows-host-agent.ps1` for default loopback or scoped `-RemoteAddress` firewall behavior and absence of `-token $Token` in the scheduled-task command.
- `go test ./...` in `host-agent/`.
