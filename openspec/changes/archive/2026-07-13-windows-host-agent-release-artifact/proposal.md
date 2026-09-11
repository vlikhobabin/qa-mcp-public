## Why

The final T4 gate found that the ignored executable beside the Go source was
stale and lacked current bridge-registration and BSL-supervision flags. The
gate had to reconstruct an ad hoc cross-build command before either station
could be bootstrapped, even though qa-mcp already has a signed self-hosted
release channel.

## What Changes

- Add one Linux-native host-agent-only artifact builder and verifier.
- Emit the Windows GUI executable, sha256 and source/toolchain provenance
  manifest into ignored output from a clean checkout.
- Verify PE architecture/subsystem, Go build metadata and required current
  registration, BSL and TestClient surface markers.
- Reuse the builder from the full signed self-hosted publisher.
- Replace installer/docs guidance that treats an ignored adjacent executable or
  a hand-written cross-build as the supported delivery path.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-self-hosted-release`: Windows host-agent release staging consumes one
  verified, provenance-bound artifact contract.

## Impact

This affects qa-mcp release tooling, host-agent delivery docs and offline
tests. It creates only ignored build artifacts during verification and does not
install software, contact Windows stations, mutate an infobase or publish a
release. The existing detached signed component manifest remains the remote
download trust anchor.
