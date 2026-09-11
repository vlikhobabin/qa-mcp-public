## Context

The gate reads `QA_MCP_LICENSE_BROKER` and runs `ai1c-license check`. The broker
source is `license/ai1c-license/` (root/`license/`), builds linux/amd64 (~9 MB).
Model A's `docker/run-host-platform.sh` already bind-mounts host identity, the
precedent for the ephemeral-container fingerprint problem.

## Goals / Non-Goals

- **Goal:** broker present + runnable in the image; host-stable fingerprint +
  persistent lease via a machine-id bind + named volume; CI ships it.
- **Non-Goal:** turning the gate ON, the activation UX (`license-activation-bootstrap`).
- **Non-Goal:** server-side config (root/`license/`).
- **Non-Goal:** modifying the broker source.

## Decisions

- **D1 — DECIDED 2026-06-29: vendor a pre-built static binary (Option A).** Commit the
  built `ai1c-license` (linux/amd64) into qa-mcp at a fixed path
  (`delivery/broker/ai1c-license`), `!`-whitelist it in `.dockerignore`, and `COPY` it to
  `/usr/local/bin/ai1c-license` in the final image stage (the gate resolves `ai1c-license`
  on `PATH` / `QA_MCP_LICENSE_BROKER`). **Rationale:** the broker is pure-Go stdlib — no
  CGO, no 3rd-party deps (`go.mod` has no `go.sum`), one `cmd/ai1c-license` target — so
  `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags='-s -w'` yields a
  fully static, stripped **6.0 MB** ELF (verified `ldd → not a dynamic executable`). The
  binary is therefore trivially reproducible and needs **no cross-repo token** in local OR
  CI builds. **Reproducibility:** `docker/refresh_broker.sh` rebuilds from root/`license`
  and writes the broker source commit + `sha256` next to the vendored binary; pin both.
  *Rejected:* **B** (release artifact from root/`license`) — needs a release pipeline in the
  other repo + a cross-repo read token; keep as a future migration if the broker gains its
  own release cadence. **C** (git submodule + `FROM golang` build stage) — needs
  private-submodule CI creds and pulls the broker SOURCE into qa-mcp (would expose it if the
  qa-mcp repo is public; the vendored *binary* ships in the public image regardless, so A
  leaks nothing extra).
- **D2 — Host-stable fingerprint via `AI1C_LICENSE_FINGERPRINT` (CORRECTED 2026-06-29).**
  The original plan said bind the host `/etc/machine-id`. Reading the broker
  (`currentFingerprint` in `internal/broker/broker.go`) shows it does **NOT** read
  `/etc/machine-id` — it hashes `os.Hostname()`, OR, if `AI1C_LICENSE_FINGERPRINT` is set,
  returns that value **verbatim** as the fingerprint. A container's hostname is random per
  run, so the correct host-stable mechanism is to **pass `AI1C_LICENSE_FINGERPRINT=<stable
  host id>`** (OS-agnostic, no bind). Linux host: the host's `/etc/machine-id` value; Windows
  host: the registry `MachineGuid` (resolved in `license-activation-bootstrap` D5). The
  compose + run docs were corrected to this; the `/etc/machine-id` bind is dropped.
- **D3 — Named volume for lease state.** Mount `qa-mcp-license:/var/lib/qa-mcp/license`
  for the broker's activation/lease cache so the lease + grace survive recreation.
  Point the broker's state dir at it.
- **D4 — Wire into compose + docs + CI.** Add the bind + volume to
  `docker-compose.thin.yml`; document the `docker run` form in the run docs; have
  `release.yml` build + include the broker (compose with `ci-nuitka-release`).
- **D5 — Gate stays OFF.** This change makes the gate *able* to pass; it does not
  enable it (that is `license-activation-bootstrap`).

## Risks / Trade-offs

- **Windows host machine-id:** Linux `/etc/machine-id` has no direct Windows
  equivalent; the activation change must define how the Windows host supplies a
  stable id. Flag here, resolve in the activation change + server config.
- **Broker build coupling to root/`license/`:** the source is cross-repo; pin the
  build (version/commit) and treat the broker as a vendored build input, not a
  modified dependency.
- **Volume permissions:** the container runs as a non-root/host uid in model A; the
  lease volume must be writable by the broker — verify.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery build | Dockerfile broker COPY (vendored) | broker present + executable in image | `ai1c-license check` runs in the built image | image smoke on `qa-mcp-thin:ch2` (tasks §4.1) | **done** | qa-mcp | — |
| Delivery config | compose machine-id bind + lease volume | host-stable fingerprint + persistent lease | restart test: same fingerprint, lease read from volume (lab) | compose + docs done; restart/fingerprint DEFERRED (lab) | **partial** | qa-mcp | — |
| CI/delivery | `release.yml` ships the broker | published image carries the broker | gate verify confirms broker present | vendored in-context → COPYed; CI-run URL deferred (tasks §2.1) | **done** | qa-mcp | — |

Residual risk: the Windows host-id story is defined by the activation change +
server config; until then the host-stable anchor is proven on a Linux host only.
