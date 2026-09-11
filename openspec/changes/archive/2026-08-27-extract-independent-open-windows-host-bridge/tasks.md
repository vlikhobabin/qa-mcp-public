## 1. Freeze the standalone bridge contract

- [x] 1.1 Define the versioned public capability/endpoint schema for health, TestClient lifecycle/relay, window, input, screenshot and required UIA primitives.
- [x] 1.2 Add Python compatibility-handshake tests for supported, missing-capability and incompatible-major responses.
- [x] 1.3 Inventory Go packages, flags, installer inputs and tests as retained standalone, private-move or removed.

## 2. Isolate retained Go implementation

- [x] 2.1 Separate lifecycle/relay/display/target/security packages from COM, BSL, agent CLI, registry, onboarding and generic platform execution dependencies.
- [x] 2.2 Register only the versioned standalone routes and remove product-specific handlers, flags, health fields and help output.
- [x] 2.3 Remove external worker/supervisor/registry bootstrap code and dependencies from the public executable build graph.
- [x] 2.4 Preserve token-file ACL, constant-time authentication, origin policy, concurrency bounds, target-window binding and owned lifecycle cleanup.

## 3. Update clients and installer

- [x] 3.1 Update Python lifecycle/display clients and doctor to negotiate the public capability contract and fail closed on incompatibility.
- [x] 3.2 Reduce the PowerShell installer to public bridge files, token, listener, log and task lifecycle with idempotent reinstall/uninstall behavior.
- [x] 3.3 Add route-absence tests proving COM, BSL, agent, Team/onboarding, path-probe and generic platform execution are unavailable.

## 4. Build and qualify exact Windows artifacts

- [x] 4.1 Run the full Go suite, Python bridge contracts, cross-build and source-bound version/hash checks.
- [x] 4.2 Install the exact release candidate on the authorized Windows target and prove launch/status/relay/read/type/click/screenshot/UIA/stop behavior.
- [x] 4.3 Exercise wrong-target, locked/disconnected desktop, failed launch and repeated cleanup recovery cases without touching unrelated 1C sessions.
- [x] 4.4 Retain sanitized exact-executable evidence and update the compatibility/runbook documentation; no protocol mapping capture is required.
