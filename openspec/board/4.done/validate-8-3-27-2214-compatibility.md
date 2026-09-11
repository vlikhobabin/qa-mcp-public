# Validate 8.3.27.2214 compatibility

## Outcome

GREEN. A genuine Vanessa TestManager capture and a `4/4` read-only qa-mcp
replay proved that `8.3.27.2214` uses the existing bundled 8.3 protocol data.
The build is recorded in `config/protocol-capture-manifest-8.3.json`; committed
capture templates were not changed.

## Evidence

- `docs/protocol-research/evidence/8-3-27-2214-compatibility-2026-08-17.md`
- focused tests: `48 passed`
- full offline suite: `933 passed, 5 skipped`
- strict OpenSpec validation: `23 passed, 0 failed`

## Cleanup

The owned TestClient, Vanessa manager, Xvfb, window manager and tcpdump
processes were stopped. The temporary user license copy was removed. The
The target cluster, RAS and Apache services were restored and the publication
responded on `127.0.0.1:8315`.
