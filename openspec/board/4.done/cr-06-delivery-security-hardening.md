# CR-06 — Delivery security & packaging hardening

## Status
4.done

## Order Index
6

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Multi-agent packaging/security review 2026-07-02, findings C5, C6, P1, P2, P3
  and host-agent minors. Full report: `docs/code-review-2026-07-02.md`.

## Summary
Two genuine exposures in the shipped product plus packaging-hygiene gaps. The
Windows host-agent is reachable from the whole LAN with a plaintext,
process-visible token, and the model-A HTTP MCP server is published with **no
authentication** on all interfaces. Also: the IP-protection compile leaks
docstrings, the verify script under-proves its claim, and the images run as root
with no healthcheck. Grouped as one "delivery hardening" session (touches Go /
PowerShell / Docker / release workflow). **Can be pulled earlier than index 6 if
the deployment is exposed to an untrusted network.**

## Problems (verified against code)

### C5 — Windows host-agent: full desktop control for a LAN attacker (MAJOR)
`host-agent/install-windows-host-agent.ps1:9` defaults `BindAddress=0.0.0.0`;
`:62-66` creates an inbound firewall `Allow` rule with **no `-RemoteAddress`
scoping** (LAN-wide). The only control is a shared bearer token in
`X-QA-MCP-Agent-Token` over **plaintext HTTP** (`main.go:72-84`), and the token is
passed as `-token $Token` in the scheduled-task action (`:56`) → visible to any
local user via Task Manager/WMI. Endpoints `/type` `/send_keys` `/click`
(`driver_windows.go:128`, no bounds check) `/screenshot` (any window by
title/hwnd/pid) give arbitrary keystrokes/clicks/screen-capture against the
logged-in desktop. (Good: it fails closed when no token is set,
`main.go:74-77`.) Minors: `/version` + `/health` are unauthenticated and leak
version/binary-SHA/foreground-HWND (`main.go:62-63,91`); token compare
`!= a.config.Token` is not constant-time (`main.go:78`); no rate limiting.

### C6 — model-A HTTP MCP server has no auth, bound to all interfaces (MAJOR)
`mcp_server.py:4395-4399` serves FastMCP streamable-HTTP with
`QA_MCP_HTTP_HOST=0.0.0.0` and **no auth layer**; `docker/run-host-platform.sh:29-33`
runs `--network host` and `docker/docker-compose.yml:9` publishes `8000:8000` (all
interfaces). Anyone who can reach host:8000 can drive the full 63-tool surface
(including write / DB-assert) with no credential. The thin path is safe
(`docker-compose.thin.yml:26`, `bootstrap.ps1:105` bind `127.0.0.1:8000`).

### P1 — Nuitka compile keeps docstrings → `.so` leaks protocol prose (MINOR)
`docker/compile_protocol.sh:39` and `docker/compile_modules.sh:60` invoke Nuitka
with no `--python-flag=no_docstrings`, so `strings qa_mcp/protocol/*.so` recovers the detailed
reverse-engineering docstrings the protection is meant to hide.

### P2 — `verify_protected_image.py` under-proves its claim (MINOR)
`docker/verify_protected_image.py:33-53` checks only: no readable `protocol/*.py`
except `__init__`, tool count == 63, and the magic-prefix `is_encrypted`. It does
**not** verify the leaf modules (`license_gate.py`/`mcp_server.py`) were
compiled/removed (the non-removable-gate invariant), that `.so` files lack
readable protocol strings, or that decryption actually succeeds. The Dockerfile
build-smoke (`Dockerfile.thin:135`) is stronger than the standalone pre-publish
script the workflow runs (`release.yml:101-104`).

### P3 — image/ops hygiene (MINOR)
Neither `Dockerfile` nor `docker/Dockerfile.thin` sets a non-root `USER` (MCP
runs as root; `run-host-platform.sh` drops uid but compose/`docker run` do not);
no `HEALTHCHECK` in either image; base images use floating tags
(`python:3.12-slim-bookworm`, `python:3.13-slim`), not digests; `Dockerfile:48`
copies `uv.lock` but builds via `pip install .` (lock unused, deps only
floor-pinned); `release.yml` pins actions to mutable major tags, no
provenance/SBOM/signing, `:latest` force-overwritten each release.

## Recommended remediation
- **C5:** scope the firewall rule to the Docker gateway subnet (`-RemoteAddress`),
  or bind `127.0.0.1` and document the Docker-Desktop routing exception; read the
  token from a file/env in the scheduled task instead of `-token` on the command
  line; use `subtle`/constant-time comparison in `withAuth`; add basic rate
  limiting; require the token on `/version` and `/health` (or trim what they
  return). Document the residual `ps`-visible `/P<password>` launch
  (`bootstrap.ps1:67`) in the runbook.
- **C6:** bind the model-A publish to `127.0.0.1` by default (match the thin
  path), or front it with an auth proxy and document it; make `0.0.0.0` an
  explicit opt-in with a startup warning.
- **P1:** add `--python-flag=no_docstrings` to both Nuitka invocations.
- **P2:** fold the gate/loader assertion (modules are `.so`-only, Nuitka-loaded),
  a `strings` scan for protocol prose, and an actual decrypt round-trip into
  `verify_protected_image.py` so the recorded pre-publish check matches the
  guarantee it prints.
- **P3:** add a non-root `USER` to both images; add a lightweight `HEALTHCHECK`
  hitting the MCP port; digest-pin base images; either consume `uv.lock` in the
  model-A build or drop the unused `COPY` and constrain top-level deps; SHA-pin
  GitHub Actions and add provenance/signing (e.g. cosign) in `release.yml`.

## Change Set
- `host-agent-network-hardening` — Windows host-agent network scope, token handling,
  endpoint auth and runbook hardening.
- `mcp-http-bind-safe-default` — model-A streamable HTTP bind/publish defaults and
  explicit unsafe-exposure opt-in.
- `protected-build-hardening` — protected-image verification, docstring stripping,
  container runtime and release workflow hardening.

## Acceptance
- Host-agent: firewall rule is subnet-scoped (or bind is `127.0.0.1`); the token
  is no longer visible on the process command line; token compare is
  constant-time; `/version`+`/health` no longer leak SHA/HWND unauthenticated —
  verified by inspecting the install script + `go test ./...` covering the auth
  path (add a test that a wrong/absent token is rejected and a hostile origin is
  refused). Document decisions in `delivery/windows-agent-runbook.md`.
- Model-A: a default `docker compose -f docker/docker-compose.yml up` binds the
  MCP to `127.0.0.1` (or requires an explicit `QA_MCP_HTTP_HOST` opt-in with a
  logged warning); README/runbook updated.
- `strings` over the compiled `qa_mcp/protocol/*.so` in the built thin image finds
  **no** protocol docstrings; `verify_protected_image.py` asserts this plus the
  gate/loader invariant and a decrypt round-trip, and the workflow's pre-publish
  step runs the stronger script.
- Both images define a non-root `USER` and a `HEALTHCHECK`; base images are
  digest-pinned; `release.yml` pins actions by SHA. `docker build` of both images
  still succeeds and `verify_protected_image.py` passes.
- No secret values printed anywhere in scripts/logs (they are not today —
  regression-guard only).

## Suggested change decomposition (for `$opsx-ff`)
- **Change 1 — `host-agent-network-hardening`** (capability: windows host agent):
  C5 (firewall scope + token handling + constant-time + endpoint auth) + go tests.
- **Change 2 — `mcp-http-bind-safe-default`** (capability: MCP HTTP transport):
  C6 (default 127.0.0.1 / explicit opt-in) + docs.
- **Change 3 — `protected-build-hardening`** (capability: protected image build):
  P1 + P2 + P3 (USER/HEALTHCHECK/pins/verify script/release workflow).

## Change 1: `host-agent-network-hardening`

### Why
The Windows host-agent grants desktop-control access and must not be reachable
from the LAN with a process-visible plaintext token.

### Goal
Make the installer and Go server fail closed by default: locally scoped network
access, hidden token source, constant-time auth, protected status/control
endpoints and documented Docker Desktop routing.

### Scope
- `host-agent/install-windows-host-agent.ps1`
- `host-agent/*.go`
- `host-agent` tests
- `delivery/windows-agent-runbook.md`

### Acceptance
- Default install is loopback or firewall-scoped to an explicit remote subnet.
- Scheduled task no longer carries the token value in process arguments.
- Missing/wrong tokens and hostile origins are rejected.
- Sensitive `/version` and health details are not leaked unauthenticated.
- `go test ./...` passes in `host-agent/`.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-host-agent-network-hardening/`

## Change 2: `mcp-http-bind-safe-default`

### Why
The model-A HTTP MCP transport exposes the full unauthenticated tool surface and
must not publish on all interfaces by default.

### Goal
Align model-A HTTP transport with the safer thin path: loopback default,
loopback Docker publish and explicit unsafe-bind opt-in with a warning.

### Scope
- `src/qa_mcp/mcp_server.py`
- `docker/docker-compose.yml`
- `docker/run-host-platform.sh`
- README or delivery Docker documentation
- focused Python/config tests

### Acceptance
- Default HTTP MCP host is `127.0.0.1`.
- Docker Compose uses host networking with `QA_MCP_HTTP_HOST=127.0.0.1` by default.
- Wildcard/non-loopback binds require an explicit unsafe opt-in and log a warning.
- Focused config tests pass.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-mcp-http-bind-safe-default/`

## Change 3: `protected-build-hardening`

### Why
The protected image should not leak docstrings or rely on a verifier that proves
less than the release claim, and the published containers/workflow need stronger
default hygiene.

### Goal
Strip protected docstrings, strengthen protected-image verification, run images
as non-root with healthchecks, pin external delivery inputs and keep release
verification authoritative.

### Scope
- `docker/compile_protocol.sh`
- `docker/compile_modules.sh`
- `docker/verify_protected_image.py`
- `Dockerfile`
- `docker/Dockerfile.thin`
- `docker/docker-compose.yml`
- `.github/workflows/release.yml`
- release/package documentation as needed

### Acceptance
- `strings` over compiled protocol modules finds no selected protocol docstrings.
- `verify_protected_image.py` checks gate/loader, strings leakage and decrypt/open
  invariants.
- Both images define non-root `USER` and `HEALTHCHECK`.
- Base images and release actions are pinned immutably.
- Docker builds and protected-image verification pass or record a concrete
  environment gap.

### Depends On
- `mcp-http-bind-safe-default`

### Related
- `openspec/changes/archive/2026-07-02-protected-build-hardening/`

## Verify
- planned — include `go test ./...` in `host-agent/`, focused Python/config tests,
  Docker builds of both images, `docker/verify_protected_image.py`,
  `openspec validate --all` and `git diff --check`; record results in
  `## Result`.

## Related
- `docs/code-review-2026-07-02.md` (C5, C6, P1, P2, P3)
- `openspec/changes/archive/2026-07-02-host-agent-network-hardening/`
- `openspec/changes/archive/2026-07-02-mcp-http-bind-safe-default/`
- `openspec/changes/archive/2026-07-02-protected-build-hardening/`
- Memory: qa-mcp public delivery prep (model-B thin, host-agent, license gate).

## Result
Implemented, verified and archived all three CR-06 changes:

- `host-agent-network-hardening`: scoped Windows host-agent exposure, moved token
  use to token files/env, added constant-time auth, Origin filtering, status
  endpoint auth and failure throttling.
- `mcp-http-bind-safe-default`: made model-A HTTP loopback by default and
  requires an explicit unsafe-bind opt-in for wildcard/non-loopback binds.
- `protected-build-hardening`: compiled protected modules without docstrings,
  strengthened protected-image verification, added non-root users and
  healthchecks, digest-pinned base images, SHA-pinned release actions, and
  removed the unused model-A `uv.lock` image copy.

Verification:

- `go test ./...` in `host-agent/windows-display-agent`
- `uv run --extra dev pytest -q tests/test_mcp_server.py tests/test_display_backend.py` — 96 passed
- `docker build -t qa-mcp:cr06 .`
- `docker build -f docker/Dockerfile.thin -t qa-mcp-thin:cr06 .`
- `docker/verify_protected_image.py` against `qa-mcp-thin:cr06` — 63 tools,
  compiled gate modules, clean protocol `.so` scan, 16 encrypted/decryptable
  bundled data files and broker present
- `strings` scan evidence retained under
  `.artifacts/openspec/protected-build-hardening/cr06-do/strings-protocol-leak-scan.txt`
- `docker image inspect qa-mcp:cr06 qa-mcp-thin:cr06` confirms `USER qa-mcp`
  and healthchecks for both images
- `openspec validate --all`
- `git diff --check`

Published in the scoped CR-06 commit.

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (C5, C6, P1, P2, P3).
- 2026-07-02T10:10:55Z accepted for delivery and decomposed into three
  OpenSpec changes.
- 2026-07-02T10:48:00Z implemented, verified, synced to specs and archived all
  CR-06 changes.
- 2026-07-02T11:05:00Z committed CR-06 delivery hardening.
- 2026-07-02 tail cleanup: tightened model-A compose so the default uses host
  networking plus `QA_MCP_HTTP_HOST=127.0.0.1` instead of defaulting the
  in-container server to wildcard with `QA_MCP_HTTP_ALLOW_UNSAFE_BIND=1`.
- 2026-07-02 tail cleanup: added delivery-config coverage for non-loopback
  HTTP binds failing closed without `QA_MCP_HTTP_ALLOW_UNSAFE_BIND=1` and
  warning when the explicit unsafe opt-in is present.
