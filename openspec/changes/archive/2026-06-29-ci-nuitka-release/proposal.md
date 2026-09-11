## Why

The protection only matters for the **published** artifact. Compiling the
protocol (`nuitka-protocol-build-stage`) and encrypting `_bundled`
(`encrypt-bundled-data`) are wired into `docker/Dockerfile.thin`, but the public
delivery is the **GHCR image built by `.github/workflows/release.yml`** on a
version tag. If CI builds an unprotected image, the protection never ships. This
change makes the released GHCR image the **protected build**.

This change touches **delivery/CI config** (`.github/workflows/release.yml`) only;
it requires **no live 1C runtime** — its evidence is a successful protected CI
build plus the same image-level checks the prior changes defined. The dev `src/`
is unchanged.

## What Changes

- `.github/workflows/release.yml` builds the thin image through the multi-stage
  Nuitka + encrypt path so the pushed `ghcr.io/vlikhobabin/qa-mcp-thin` (`:tag` +
  `:latest`) is the protected build (compiled `protocol/`, encrypted `_bundled`).
- The **AES-GCM key** is supplied to the CI build from a **GitHub secret** (build
  arg / secret file), never committed; the same key is embedded in the compiled
  helper and used by the encrypt step.
- The **local `docker build -f docker/Dockerfile.thin` path keeps working** (a
  dev/default key or a documented build-arg), so local protected builds remain
  possible without CI.
- Document the **added build time** (Nuitka compile + encrypt) in the release/CI
  docs.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: the **released** GHCR thin image is the protected build —
  CI compiles the protocol to `.so` and encrypts the bundled data, with the
  encryption key injected from a CI secret, and the local build path still
  produces a working (protected) image.

## Impact

- **CI/delivery:** `.github/workflows/release.yml` (build path + a new key secret
  reference); release/CI docs note the added build time and the key-secret setup.
- **No `src/` code change** beyond what the prior two changes already introduced.
- **Depends on** `nuitka-protocol-build-stage` and `encrypt-bundled-data` (CI just
  invokes the build path they define). Pairs with card 121 (broker-in-image is
  wired into the same release workflow by card 121's own change).
