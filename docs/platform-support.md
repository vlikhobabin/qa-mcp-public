# Platform-support factory

How qa-mcp adds support for a new 1C platform version — as a systematic, mostly-deterministic process
rather than an ad-hoc investigation each time.

## The one idea

After the multi-version architecture (epic 112) the wire protocol is **version-generic**: the live version
string is injected at runtime from `PLATFORM_ROOT` / `QA_MCP_PLATFORM_VERSION` (in `bootstrap_synth`, `replay`,
`foreground`). Support keys on the platform **major-minor family** — `SUPPORTED_VERSION_KEYS = ("8.3", "8.5")` in
`src/qa_mcp/_bundled/__init__.py`. The exact builds live in a per-family manifest
`config/protocol-capture-manifest-<family>.json` (`platform_version` baseline + `compatible_platform_versions[]`).

So there are two kinds of "add a version":

* **Case A — a build of an already-supported family whose wire did not move** (e.g. any new `8.3.27.x`). This is a
  **data + config + validate** operation, no protocol-code change: boot the build, run the live-regression, and on
  GREEN append it to the family manifest.
* **Case B — a new family, or a build whose validate goes RED** (the wire actually moved). This is real
  development (lab, capture, version-conditional code) and is driven as an OpenSpec card through headless Codex.

## The engine — `python -m qa_mcp.platform_support`

Composition over the existing `regression` / `versioning` / `_bundled` machinery; it adds no protocol knowledge.

| command | what it does |
| --- | --- |
| `probe <ver>` | offline classify → `already` \| `A` \| `B` \| `unknown` (add `--json`) |
| `validate <ver>` | boot `/TESTCLIENT` on the build + run `qa_mcp.regression --include-write` → GREEN/RED verdict; writes `runtime/platform-support/<ver>/verdict.json` |
| `bless <ver>` | append a GREEN same-family build to its manifest's `compatible_platform_versions` (refuses non-A / non-GREEN) |
| `matrix [--validate]` | probe (and optionally live-validate case-A) every installed `/opt/1cv8/x86_64/*` build |

`validate` points the harness at the build **two ways that must agree**: the cloned env-file `PLATFORM_ROOT`
picks the *binary* to boot; the process `QA_MCP_PLATFORM_VERSION` picks the *handshake version string* the synth
declares. The lab OData URL must be supplied (default `http://127.0.0.1:8316/vanessa_client/odata/standard.odata`);
`Settings.odata_url` is empty by default.

Prerequisites (dev box): the platform installed under `/opt/1cv8/x86_64/<version>/`, Apache up on :8316, Xvfb +
`matchbox-window-manager` available, and the lab fixture IB (`/opt/1c-dev/vanessa_client`). Runs are **sequential**
— a validate monopolizes the TestClient (port 15381), Apache and the Xvfb display.

## The trigger — «добавить поддержку X»

The entry point is the `qa-add-platform` skill (`skills/qa-add-platform/SKILL.md`, delivered to agents via the
per-machine `.codex/skills/qa-add-platform` symlink). On a request to add a
platform version it: `probe` → for **Case A** runs `validate` → on GREEN `bless` + doc/support-list update + a
scoped commit; for **Case B** seeds a card and hands it to headless Codex.

Front doors: the foreground agent runs the engine commands directly (it discovers this flow from this doc +
project memory). To drive the whole router from **Codex**, use the launcher — `./bin/codex exec '$qa-add-platform
8.3.27.XXXX'` (unattended) or interactive `./bin/codex` — which composes a CODEX_HOME so the Codex session loads
qa-mcp's skills (`qa-add-platform`, `opsx-*`). A plain `codex` in this dir does NOT (Codex has no per-dir
auto-config).

### Case A — deterministic (no code)

```bash
python -m qa_mcp.platform_support validate 8.3.27.XXXX
# GREEN:
python -m qa_mcp.platform_support bless    8.3.27.XXXX --notes "validated GREEN <date>"
python -m qa_mcp.regression.versioning --platform-root /opt/1cv8/x86_64/8.3.27.XXXX   # expect OK
```

Then update the supported-build list (`README.md`, `delivery/*`) and make a scoped commit (via `$opsx-pub` on a
card, or directly). Commit/push only when asked.

Batch every installed build at once: `python -m qa_mcp.platform_support matrix --validate`.

### Case B — new family / RED → headless Codex

```bash
# 1. seed a card from the template, fill the version/family + the RED evidence:
cp docs/platform-support-new-family-card-template.md \
   openspec/board/1.backlog/<NN>-<date>-platform-<family>-support.md
#    …edit placeholders…
# 2. deliver it unattended (ff -> do -> review -> pub) through Codex:
DRY_RUN=1 scripts/deliver-platform-support.sh <NN>-<date>-platform-<family>-support.md   # preview
scripts/deliver-platform-support.sh          <NN>-<date>-platform-<family>-support.md    # run (WRITE + PUSH)
```

`scripts/deliver-platform-support.sh` composes a CODEX_HOME (qa-mcp `.codex/config.toml` + `.codex/skills`, both
carrying the `opsx-deliver` and `qa-add-platform` skills, + the operator's ChatGPT auth) and runs
`$opsx-deliver <card>` with `--sandbox danger-full-access -c approval_policy=never`. `$opsx-deliver` runs the full
pipeline **including pub → a scoped git commit and push**.

Caveat: a genuine wire move needs a live capture step (tcpdump + Vanessa TestManager, licensed user, real `$HOME`)
that headless Codex cannot perform — per `docs/capture-refresh-runbook.md`. Structure the card so the capture is
pre-bundled or its `$opsx-do` calls the lab tooling; otherwise finish the capture by hand and re-run validate.

## Snapshot (2026-08-17)

Supported families: `8.3` (baseline `8.3.27.2130`) and `8.5` (baseline `8.5.1.1343`, reusing the 8.3 protocol data
via `PROTOCOL_DATA_FALLBACKS`). Blessed 8.3 builds: `1606, 1644, 1688, 1719, 1786, 1936, 2074, 2130, 2170, 2214`.
Build `2214` was validated with a genuine Vanessa open-list capture and a GREEN `4/4` read-only UI replay of the
existing bundled 8.3 corpus; see `docs/protocol-research/evidence/8-3-27-2214-compatibility-2026-08-17.md`. Earlier
builds retain their existing full-regression evidence.

## See also

- `docs/live-regression.md` — the live-regression harness this factory drives.
- `docs/capture-refresh-runbook.md` — the RED / re-capture procedure (Case B).
- `skills/qa-add-platform/SKILL.md` — the entry skill contract (Codex-delivered via `.codex/skills`).
- `bin/codex` — the qa-mcp Codex launcher (composes a CODEX_HOME so a Codex session here loads qa-mcp's skills).
- `docs/platform-support-new-family-card-template.md` — the Case-B seed card.
