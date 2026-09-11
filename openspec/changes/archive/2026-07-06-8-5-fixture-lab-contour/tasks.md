## 1. Stand up the 8.5 fixture infobase

- [x] 1.1 Copy the 8.3 `vanessa_client` file IB (`/opt/1c-dev/vanessa_client/1Cv8.1CD`)
  to a throwaway path `/opt/1c-dev/vanessa_client_85/`, leaving the original
  untouched (gitignored runtime; never committed).
- [x] 1.2 Convert the copy to 8.5 headless: `8.5/1cv8 DESIGNER /IBConnectionString
  "File=…vanessa_client_85;" /N"Администратор" /UpdateDBCfg /DisableStartupDialogs
  /DisableStartupMessages` under `xvfb-run` (exit 0; config-reorg artifacts written).

## 2. Confirm the 8.5 TestClient boots and renders

- [x] 2.1 Boot `8.5/1cv8 ENTERPRISE … /TESTCLIENT -TPort 15381` against the
  converted copy on an explicit Xvfb display (no Apache stop — the copy is a
  separate file). Verify it listens (`ss -ltn | grep :15381`) with empty
  `testclient.out` (no license/conversion error).
- [x] 2.2 Screenshot the rendered managed UI (`scrot`) and retain it under
  `docs/protocol-research/evidence/card114-8-5-lab-gate-2026-06-25/`.

## 3. Document the 8.5 lab-boot recipe

- [x] 3.1 Added an "Adding a new platform version (8.5) — the lab boot" section to
  `docs/capture-refresh-runbook.md`: the copy → convert → boot-on-explicit-display
  flow, the no-Apache-stop note, the `/N`-no-`/P` gotcha, and the
  `PLATFORM_ROOT`/`QA_MCP_PLATFORM_VERSION=8.5` wiring into P0's resolvers.
- [x] 3.2 Recorded that the *fixture form open* + capture is the adjacent change
  `8-5-genuine-action-capture` (this change proves the contour + desktop render).

## 4. Verification

- [x] 4.1 Gate evidence: 8.5 TestClient listening on :15381 + rendered demo
  desktop screenshot (2026-06-25). See the Verification Matrix in `design.md`.
- [x] 4.2 Offline suite stays green (497) and the 8.3 contour is unchanged — this
  change touches only docs + gitignored runtime (no `src/` edits).
