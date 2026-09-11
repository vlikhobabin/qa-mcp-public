## Why

The startup gate (`license-gate-startup`) calls `ai1c-license check`, but the thin
image carries no broker and has no stable license anchor. The broker builds for
linux/amd64 (~9 MB), so it can ship in the image. The model-B wrinkle is that a
thin container is **ephemeral**: its `machine-fingerprint-v1` and lease state reset
every run, so a naive in-container broker never holds a per-user lease. This change
ships the broker and gives it a **host-stable identity + persistent lease state**,
mirroring model A's `run-host-platform.sh`, which already bind-mounts host identity.

This change touches **delivery/build config** (Dockerfile, compose, run docs, CI)
and requires **no live 1C runtime**; its evidence is the broker present + runnable
in the image and the identity/lease mounts documented. The gate stays OFF until the
activation change turns it on.

## What Changes

- **Build the broker** for linux/amd64 (`GOOS=linux GOARCH=amd64 go build
  ./cmd/ai1c-license` from `license/ai1c-license/`) and **COPY it into the thin
  image** at a known path the gate's `QA_MCP_LICENSE_BROKER` points to.
- **Host-stable fingerprint:** bind-mount the host `/etc/machine-id` (Linux host) /
  a host-provided stable id into the container so the broker fingerprints the
  **host**, not the ephemeral container → stable + per-user. Wire it into
  `docker-compose.thin.yml` + the run docs.
- **Persistent lease state:** mount a named volume
  (`qa-mcp-license:/var/lib/qa-mcp/license`) for the broker's activation/lease cache
  so the lease + offline-grace survive container recreation.
- **CI:** the release workflow builds + ships the broker with the image (composing
  with card 122's `ci-nuitka-release` edit to `release.yml`).
- The gate itself stays **OFF by default** (turning it ON is the next change).

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-license-gate`: the thin delivery ships the `ai1c-license` broker and a
  **persistent, host-stable license anchor** — the broker fingerprints the host
  (not the ephemeral container) via a bind-mounted host machine-id and caches its
  lease in a named volume, so a per-host lease + offline grace survive container
  restarts.

## Impact

- **Delivery/build:** `docker/Dockerfile.thin` (build + COPY the broker);
  `docker/docker-compose.thin.yml` (machine-id bind + `qa-mcp-license` volume);
  the run docs (`docker/README.md` / model-B section); `.github/workflows/release.yml`
  (build/ship the broker — compose with `ci-nuitka-release`).
- **Cross-repo input:** the broker **source** lives at `license/ai1c-license/`
  (root/`license/` workspace); this change builds it for the image but does not
  modify it.
- **No `src/` code change** (the gate already reads `QA_MCP_LICENSE_BROKER`).
- **Depends on** `license-gate-startup`. **Out of scope:** activation + turning the
  gate ON (`license-activation-bootstrap`), the server-side config (root/`license/`).
