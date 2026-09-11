# Capture refresh runbook — surviving platform/configuration protocol drift

**Roadmap card 111, item 4.** qa-mcp drives 1C by replaying a captured **irreducible handshake** + per-element
**frame templates**. Those bytes are faithful to ONE platform protocol version. A platform upgrade can move the
handshake or a field offset. This runbook is how you detect that and re-baseline without committing raw capture
payloads.

> **The handshake shape is bound to the platform build, NOT to the configuration.** `read_list_grid` on
> `Справочник.Валюты` was proven positive on **[redacted third-party configuration]** (2026-07-08, historical-user .201) using the **bundled 8.3
> capture** — the same capture that reads demo10413 — so there is no config-specific handshake to re-capture.
> A live `manager-handshake-moved` / "client ACK GUID not found after manager frame 3" is, in practice,
> **INTERMITTENT session state** (the client serves one manager session at a time — a stale/racing connection makes
> the next handshake fail; just retry) or an **environment** problem, NOT genuine per-configuration protocol drift.
> Before assuming a capture refresh is needed, rule out: (1) a wrong 1C user so the TestClient bound its TPort then
> died (`/Out` = `Пользователь ИБ не идентифицирован`); (2) a wrong `QA_MCP_HOST_AGENT_WINDOW` so the F5 list
> refresh could not reach the client window (`row_count:0, "no display backend was reachable"`); (3) an unreachable
> host-agent (e.g. driving cross-LAN when its port is firewalled — drive locally instead). Only refresh the capture
> after a genuine platform-protocol move (the drift detector + live-regression below), not for a new configuration.

## 1. The signal — do I need to refresh?

Two independent signals; refresh when the live one fails:

- **Cheap, no boot — the drift detector.** `python -m qa_mcp.regression.versioning` compares the live platform
  version (from `PLATFORM_ROOT` / `QA_MCP_PLATFORM_VERSION`) against the stamped baseline and any
  `compatible_platform_versions` for that version family (the manifest is **per-version**:
  `config/protocol-capture-manifest-<version>.json`, e.g. `…-8.3.json`; the detector auto-selects the file
  matching the live family). A `VERSION` verdict means "live platform is not yet captured or marked compatible" —
  captures *may* be stale, not proof they are.
- **Authoritative — the live-regression harness.** `python -m qa_mcp.regression` actually replays against a real
  TestClient. **GREEN ⇒ the captures still work** on this platform (even if the version differs — then just
  re-stamp, see §4). **RED ⇒** the protocol moved; refresh the captures (§3).
- **Target-specific — the manager-handshake preflight.** When a list-read setup fails at manager frame 3, qa-mcp
  reports `manager-handshake-moved` instead of a generic table-resolution failure. That means the selected capture is
  not proven for the requested platform/configuration/transport and the refresh procedure below is required.

Decision table:

| drift detector | live-regression | action |
| --- | --- | --- |
| OK | GREEN | nothing — baseline is current |
| VERSION | GREEN | platform bumped but compatible → **re-stamp** the manifest (§4) |
| VERSION | RED | protocol changed → **refresh captures** (§3), then re-stamp |
| TEMPLATE / MISSING | (any) | a committed template was edited/removed without re-stamping → revert the edit, or re-capture + re-stamp |

## 2. What is versioned/tagged (the artifacts)

`config/protocol-capture-manifest-<version>.json` (one per platform family, e.g. `…-8.3.json`) records the
baseline platform version, validated-compatible platform versions and a content hash of each template:

- **`manager_frame_templates`** (committed, hash-enforced) —
  `docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/manager_frame_templates.json`.
  The irreducible handshake + the UTF-16 ManagedForm frame templates that everything replays. **This is the
  version-critical artifact.**
- **`value_read_templates`** (runtime, hash NOT enforced) —
  `runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json`. Regenerated per
  machine (git-ignored); recorded for reference only.
- **`capture-metadata.json` sidecars** (small, reviewed) — sanitized labels for a capture/template set:
  `capture_id`, `platform_build`, `configuration.name`, optional configuration version/vendor, capture/template paths
  and notes. These files are safe to commit because they do not contain raw TCP payloads, credentials, screenshots,
  infobase dumps or customer data.

## 3. Refresh procedure (when live-regression or manager-handshake preflight goes RED)

This re-records the genuine protocol against the target platform/configuration. It is the involved path — budget a
focused session and keep raw data under ignored runtime directories.

1. **Pin the target.** Set `PLATFORM_ROOT=/opt/1cv8/x86_64/<new-version>` in the target env file and record the
   target configuration label, for example `8.3.27.2130` / `Бухгалтерия 3.0` / `[redacted third-party configuration]`.
2. **Capture genuine traffic.** Boot the genuine Vanessa TestManager + a TestClient and capture the wire while a
   minimal scenario runs (open a list → read a value), using the established tooling:
   - `tools/protocol-research/capture_session.sh` (manager + `tcpdump` on `lo`, the client TPort range) — see the
     genuine-capture recipe in memory `[[genuine-action-capture-recipe]]` and
     `docs/protocol-research/methodology.md`.
   - Convert the pcap to normalized traffic and rebuild the frame templates:
     `tools/protocol-research/build_tm_v1_open_template.py` (+ `analyze_capture.py` to sanity-check frames).
3. **Prepare sanitized capture metadata.**
   ```bash
   python tools/protocol-research/prepare_capture_metadata.py \
     --output runtime/protocol-research/captures/<capture-id>/capture-metadata.json \
     --capture-id <capture-id> \
     --platform-build 8.3.27.2130 \
     --configuration-name "Бухгалтерия 3.0" \
     --configuration-vendor "[redacted third-party configuration]" \
     --capture-dir runtime/protocol-research/captures/<capture-id> \
     --manager-templates runtime/protocol-research/templates/<capture-id>/manager_frame_templates.json \
     --check
   ```
   Move only the reviewed sidecar/template metadata into git when appropriate; raw pcaps, traffic logs, screenshots
   and platform logs stay ignored.
4. **Replace the committed templates** at the `manager_frame_templates` path above with the freshly-built
   `manager_frame_templates.json`. Keep the dated directory convention (`<YYYYMMDD>-…`) and update
   `DEFAULT_TEMPLATES` in `src/qa_mcp/mcp_server.py` + `TEMPLATE_SPEC` in
   `src/qa_mcp/regression/versioning.py` if the path changes.
5. **Regenerate the value-read templates** into `runtime/…/tm-v1-open-plus-valueread/` (the `read_form_descriptor`
   sweep) — these are local/runtime, not committed.
6. **Re-stamp** the manifest (§4) and **validate** (§5).

## 4. Re-stamp the manifest

After a compatible bump (GREEN) or a refresh (§3):

```bash
python -m qa_mcp.regression.versioning --stamp --notes "refresh for platform <new-version>"
```

This records the live platform version + the current template hashes into the per-version manifest for the live
family (`config/protocol-capture-manifest-<version>.json`; pass `--version <key>` to target a specific family).
Commit that file. `python -m qa_mcp.regression.versioning` should then report `OK`.

## 5. Validate

```bash
python -m pytest -q                              # offline: versioning + harness logic
python -m qa_mcp.regression.versioning           # drift detector → OK
python -m qa_mcp.regression                       # live-regression → GREEN 4/4 (the real proof)
```

A GREEN live-regression on the re-stamped baseline closes the refresh.
For target-specific list reads such as [redacted third-party configuration] `Справочник.Валюты`, retain a sanitized MCP transcript or
QA/TestClient bundle showing the config-matched capture was selected and visible row(s) were returned. If the target
host is unavailable, record a provider gap instead of claiming the positive read.

## CI / cron

- `python -m qa_mcp.regression.versioning --strict` — exit non-zero on ANY drift (version included). Use as a fast
  gate that forces an explicit re-stamp decision after a platform bump.
- `python -m qa_mcp.regression` — the authoritative live gate (boots a client). The drift detector tells you
  *where to look* when it goes red.

## Adding a new platform version (e.g. 8.5)

**Re-capturing the whole corpus per platform release is the LAST resort, not the default.** A new platform
usually does NOT move the wire protocol; the cheap, correct first step is to **validate the existing (8.3)
implementation on the new platform with the e2e harness, and only re-capture what actually goes red.** Confirmed
for **8.5.1.1343** (epic 112): the 8.3 bundled captures/templates REPLAY on 8.5 as-is — the only code change
needed was a one-field version string (see `bootstrap_synth.resolve_synth_platform_version`).

### Validate-first (preferred)

1. Boot the new-platform client and run the e2e against it with the **8.3 bundled data** — decouple the synth
   version (which must match the live client) from the capture set (which can stay 8.3):
   ```bash
   # PLATFORM_ROOT=8.5 → synth declares 8.5; QA_MCP_PLATFORM_VERSION UNSET → captures resolve to _bundled/8.3
   PLATFORM_ROOT=/opt/1cv8/x86_64/8.5.1.1343 \
     QA_MCP_ODATA_URL=http://127.0.0.1:8316/vanessa_client/odata/standard.odata/ \
     python -m qa_mcp.regression --env <8.5-env-with-PLATFORM_ROOT> --include-write
   ```
2. **GREEN ⇒ no re-capture.** Just bless the version (re-stamp): `python -m qa_mcp.regression.versioning --stamp
   --version <key> --platform-root <new root>` (writes `config/protocol-capture-manifest-<key>.json`). The synth
   already injects the live version automatically (`PLATFORM_ROOT` / full `QA_MCP_PLATFORM_VERSION`).
3. **RED on a specific capability ⇒ re-capture ONLY that one** and bundle it (below). Don't redo the whole corpus.

8.5 status (2026-06-25): the **full live-regression is GREEN on 8.5 with the 8.3 data** (`--include-write`,
7/7): protocol-drift, data-layer (OData), assert, open, read/introspect, **write_by_label** and the **UI→DB
write_persisted** roundtrip all pass. No re-capture was needed — the only code was two one-field version
injections (the synthesized bootstrap + the card-101 foreground replay both declare the LIVE platform version
instead of the captured 8.3 one), plus a clean-state Escape sweep before the write so the foreground starts from
the start page regardless of prior tabs. The wire protocol did NOT move.

### Re-capture flow (only when validate-first goes red)

First stand up the lab contour. Proven 2026-06-25 for **8.5.1.1343**:

1. **Convert a *copy* of the fixture infobase** (keep the original untouched — the new platform does a one-time
   DB conversion):
   ```bash
   cp -a /opt/1c-dev/vanessa_client/1Cv8.1CD /opt/1c-dev/vanessa_client_85/1Cv8.1CD   # gitignored runtime
   xvfb-run -a /opt/1cv8/x86_64/8.5.1.1343/1cv8 DESIGNER \
     /IBConnectionString 'File="/opt/1c-dev/vanessa_client_85";' /N"Администратор" \
     /UpdateDBCfg /DisableStartupDialogs /DisableStartupMessages /Out convert.out -NoTruncate
   ```
   **Gotcha:** pass `/N"<user>"` with **no** `/P` — an empty `/P""` fails with «Пользователь ИБ не идентифицирован».
2. **Boot the new-platform `/TESTCLIENT` against the copy** on an explicit Xvfb display (so you can screenshot).
   **No `apache2 stop` needed** — the copy is a *separate file*, so it does not contend with the 8.3 OData
   publication holding the original (unlike the same-version boot in §3):
   ```bash
   Xvfb :91 -screen 0 1280x1024x24 -nolisten tcp &
   DISPLAY=:91 /opt/1cv8/x86_64/8.5.1.1343/1cv8 ENTERPRISE \
     /IBConnectionString 'File="/opt/1c-dev/vanessa_client_85";' /N"Администратор" \
     /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages /Out tc.out -NoTruncate &
   ```
   Confirm it listens (`ss -ltn | grep :15381`) with an empty `tc.out`, and screenshot the rendered desktop.
3. **Capture the genuine corpus on the new version** (the long pole) and bundle it with
   `python scripts/bundle_runtime_assets.py --version 8.5 --source-captures … --source-manager-templates … …`,
   then stamp `config/protocol-capture-manifest-8.5.json` with `… versioning --stamp --platform-root <8.5 root>`.

### Capture-driver caveat (run the manager as the licensed user — mind `HOME`)

Recording genuine manager↔client traffic needs a 1C process speaking the new-version **manager** protocol to
the new-version TestClient — the Vanessa TestManager (`/TestManager`), since qa-mcp's own replay can't drive a
version it hasn't captured yet. The Vanessa TestManager **does run on 8.5** (verified 2026-06-25: MCP port up in
~3 s, no license error). **Critical gotcha:** the 1C software license is stored **per-user** under
`$HOME/.1cv8/1C/1cv8/conf/*.lic`, so the manager MUST be launched as the licensed OS user with `HOME` pointing at
that user's home. If a launcher overrides `HOME` (e.g. to a runtime/scratch dir — as
`vanessa-mcp/bin/start-vanessa-manager.sh` does via `VANESSA_HOME`), the platform looks for the license in the
wrong place and dies with «Не найдена лицензия» — which looks like a mode/version licensing limit but is **not**:
it is purely the `HOME`-relative license lookup. Launch `/TestManager` with the real `HOME` (or point
`HOME`/`VANESSA_HOME` at the licensed user's home) and the license binds in every mode.
