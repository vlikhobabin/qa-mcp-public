## 1. Build + ship the broker in the thin image

- [x] 1.1 Built `ai1c-license` (linux/amd64, `CGO_ENABLED=0 … -trimpath -ldflags='-s -w'`)
  → **static, stripped, 6.0 MB** (`ldd → not a dynamic executable`); **vendored** at
  `delivery/broker/ai1c-license`. Pinned in `delivery/broker/SOURCE.md` (source commit
  `1920ce2`, root HEAD `69073d8`, `go1.26.0`, sha256 `61c4cfd…`) + `ai1c-license.sha256`.
  `docker/refresh_broker.sh` rebuilds + re-pins (reproduced the identical sha256). Source
  not modified.
- [x] 1.2 `docker/Dockerfile.thin` `COPY delivery/broker/ai1c-license
  /usr/local/bin/ai1c-license`, `chmod 0755`, `ENV QA_MCP_LICENSE_BROKER=` that path
  (+ `AI1C_LICENSE_LEASE_PATH`/`KEYSET_PATH` → the lease volume). `.dockerignore`
  whitelists the binary (SOURCE.md/.sha256 stay out). Build smoke asserts the broker runs
  + emits the `ai1c.license.check.output.v1` schema.

## 2. CI ships the broker

- [x] 2.1 No CI build step needed — the broker is **vendored in-context**
  (`delivery/broker/ai1c-license`), so the existing `release.yml` protected build COPYs
  it directly (no cross-repo token). Added a note in `release.yml` and a broker
  presence+executable assertion to the pre-publish gate `docker/verify_protected_image.py`
  (composes with `ci-nuitka-release`). **CI run URL DEFERRED to the first tagged release.**

## 3. Host-stable identity + persistent lease

- [x] 3.1 `docker/docker-compose.thin.yml`: added the `/etc/machine-id:ro` bind + the
  named volume `qa-mcp-license:/var/lib/qa-mcp/license` (declared the top-level volume),
  **commented** since the gate is OFF by default (uncomment when enabling). The
  Windows/Docker-Desktop host has no `/etc/machine-id` → flagged as defined by the
  activation change (Ch3). The image bakes `AI1C_LICENSE_LEASE_PATH`/`KEYSET_PATH` →
  `/var/lib/qa-mcp/license` and `mkdir`s it.
- [x] 3.2 Documented the `docker run` form (machine-id bind + lease volume + gate env) in
  `docker/README.md` (new "Product license broker" section, distinct from the 1C license).
- [x] 3.3 **DEFERRED to `license-activation-bootstrap` lab gate:** lease-volume writability under the container run uid (mirror
  model A's `run-host-platform.sh`) needs a real activation + the volume mounted in the
  lab. The image dir `/var/lib/qa-mcp/license` exists; full writability is the lab gate.

## 4. Verification

- [x] 4.1 Image smoke (built `qa-mcp-thin:ch2`, **368 MB**): `ai1c-license check
  --component qa-mcp --json` runs IN the image → `ai1c.license.check.output.v1` /
  `not_licensed` / `no_lease`, exit 10 (correct fail-closed). The pre-publish gate
  `docker/verify_protected_image.py` passes: **62 tools, protocol .so-only, 16 bundled
  files ciphertext, license broker present** (exit 0).
- [x] 4.2 **DEFERRED to `license-activation-bootstrap` lab gate:** restart test — with
  `AI1C_LICENSE_FINGERPRINT` + the lease volume the broker computes the same host
  fingerprint and reads its cached lease after container recreation. Needs the lab + a
  real activation (pairs with 3.3 and the activation change).
- [x] 4.3 Gate stays **OFF** in this change (`QA_MCP_LICENSE_GATE` unset → the gate code
  path is never entered; enabling it is `license-activation-bootstrap`). Offline `pytest`
  **546 passed** (no `src/` change).
