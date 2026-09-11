## Why

P0 (card 113) made qa-mcp select its bundled protocol assets per platform
version and left an **empty `_bundled/8.5/` slot** — because the 2026-06-25
feasibility probe showed 8.5 *moved the protocol* (the 8.3 handshake replay
fails at manager frame 3), so 8.5 needs a full **re-capture** (P2/card 115), not
a re-stamp. A re-capture needs a working **8.5 lab**: a genuine TestClient that
renders the `lTestClient` fixture and whose wire traffic can be captured. This
change stands up that substrate — the contour P2 runs against — without
disturbing the live 8.3 contour.

## What Changes

- Establish an **8.5 fixture infobase** by converting a *copy* of the 8.3
  `vanessa_client` file IB to 8.5 (one-time `DESIGNER /UpdateDBCfg` conversion;
  the original 8.3 IB stays untouched). The copy lives at
  `/opt/1c-dev/vanessa_client_85/` and carries the `Обработка.lTestClient`
  fixture for free.
- Confirm an **8.5 `/TESTCLIENT` boots** against it under Xvfb with a valid
  (developer) license and renders the managed UI. Gate proven 2026-06-25:
  listening on the TPort in ~3 s, empty `testclient.out`, demo desktop rendered
  (evidence screenshot retained).
- **Document the 8.5 lab-boot recipe** (an 8.5 analogue of the
  `linux-native-testclient-xvfb` recipe) so capture runs are repeatable: boot
  against a *copy* on an explicit Xvfb display, no Apache stop required (the copy
  is a separate file → no file-IB version contention with the 8.3 OData
  publication).
- No package `src/` code changes — this is lab/runtime substrate + docs. No
  infobase mutation beyond the throwaway 8.5 copy.

## Capabilities

### New Capabilities
<!-- none — this extends the existing protocol-lab capability -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: a repeatable **8.5 platform lab contour** (a converted
  fixture infobase carrying `lTestClient` + a documented headless TestClient
  boot) exists alongside the 8.3 contour, as the substrate the P2 re-capture
  records against. Opening and capturing the fixture *form* itself is the
  adjacent change `8-5-genuine-action-capture`.

## Impact

- Runtime/lab (gitignored, never committed): `/opt/1c-dev/vanessa_client_85/`
  (the converted 8.5 fixture IB); platform `/opt/1cv8/x86_64/8.5.1.1343`;
  `xvfb-run` + `matchbox-window-manager` + `scrot`.
- Docs: an "8.5 lab boot" section in `docs/capture-refresh-runbook.md` (or a
  sibling note) — the 8.5 analogue of the native-TestClient-under-Xvfb recipe.
- Evidence: `docs/protocol-research/evidence/card114-8-5-lab-gate-2026-06-25/`
  (gitignored runtime evidence — boot screenshot).
- No `src/` code; the offline suite and the 8.3 runtime path are unchanged.
